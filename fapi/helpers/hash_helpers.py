import bcrypt

def hash_pass(password:str)-> str:
    hashed=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_pass(typed_pass,hashed_pass):
    return bcrypt.checkpw(typed_pass.encode("utf-8"),hashed_pass.encode("utf-8"))