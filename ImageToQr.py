import qrcode
import base64
import os
import zlib

def compress_file(file_path):
    """
    Compresses the file data using zlib.

    :param file_path: Path to the input file.
    :return: Compressed binary data.
    """
    with open(file_path, "rb") as file:
        binary_data = file.read()
    compressed_data = zlib.compress(binary_data)
    return compressed_data

def split_data(data, chunk_size):
    """
    Splits data into chunks of the specified size.

    :param data: Binary data to split.
    :param chunk_size: Size of each chunk in bytes.
    :return: List of data chunks (Base64 encoded).
    """
    chunks = [
        base64.b64encode(data[i:i + chunk_size]).decode("utf-8")
        for i in range(0, len(data), chunk_size)
    ]
    return chunks

def file_to_qr(file_path, output_dir, chunk_size=2000):
    """
    Converts a compressed file's binary data into multiple QR codes.

    :param file_path: Path to the input file.
    :param output_dir: Directory to save the generated QR codes.
    :param chunk_size: Maximum size of data per QR code (in bytes).
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Compress the file
    compressed_data = compress_file(file_path)

    # Split the compressed data into chunks
    chunks = split_data(compressed_data, chunk_size)

    # Generate a QR code for each chunk
    for index, chunk in enumerate(chunks):
        qr = qrcode.QRCode(
            version=None,  # Automatically adjust the size
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(chunk)
        qr.make(fit=True)

        # Save the QR code image
        output_path = os.path.join(output_dir, f"output_qr_{index + 1}.png")
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save(output_path)
        print(f"QR code saved to {output_path}")

    print(f"Total QR codes generated: {len(chunks)}")

# Example usage
if __name__ == "__main__":
    # Reduce chunk_size to avoid exceeding QR code capacity
    file_to_qr("1.png", "output_qr_codes", chunk_size=900)