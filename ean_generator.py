EAN = "7702305100562"

def ean_checksum(code: str) -> int:
    digits = [*map(int, reversed(code))]
    even, odd = digits[0::2], digits[1::2]
    number = sum(odd) + sum(even) * 3
    return (10 - number) % 10

print("Dígito de control:", ean_checksum(EAN))