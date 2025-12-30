import traceback
import sys
import os

# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

try:
    print("--- Diagnostic starting ---")
    import passlib
    from passlib.context import CryptContext
    import bcrypt

    print(f"Passlib version: {passlib.__version__}")
    print(f"Bcrypt library version: {getattr(bcrypt, '__version__', 'unknown')}")

    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def test_hashing(pw):
        print(f"Testing PBKDF2 hashing for: '{pw}' (type: {type(pw)}, len: {len(pw)})")
        try:
            h = pwd_context.hash(pw)
            print(f"  SUCCESS: {h[:20]}...")
            return h
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            return None

    h = test_hashing("test123")
    if h:
        print(f"Verifying hash: {pwd_context.verify('test123', h)}")


except Exception as e:
    print(f"DIAGNOSTIC CRASHED: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
