import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from pyzbar.wrapper import ZBarSymbol

from misc.async_wraps import run_blocking_cpu


def detect_cv(buf):
    # read the QRCODE image

    img = cv2.imread(buf)

    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()

    # detect and decode
    data, bbox, straight_qrcode = detector.detectAndDecode(img)

    # if there is a QR code
    if bbox is not None:
        print(f"QRCode data:\n{data}")
    return data


def detect(buf):
    im = Image.open(buf)
    decoded = decode(im)
    # print(detect_cv(buf))
    if decoded:
        return decoded[0].data.decode('utf-8')
    return None


async def async_detect(buf):
    return await run_blocking_cpu(detect, buf)


if __name__ == '__main__':
    print(sorted(ZBarSymbol.__members__.keys()))
