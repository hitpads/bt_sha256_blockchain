from sha256 import sha256

if __name__ == "__main__":
    message = "AITU"
    print("message:", message)
    print("SHA-256 hash:", sha256(message))
