from model.image_record import ImageRecord


class ImageRecordService:

    def __init__(self, repository):
        self.repository = repository

    def createImage(self, image: ImageRecord) -> ImageRecord:
        if not (image.format == "PNG" or image.format == "JPEG"):
            raise ValueError("Image format must be PNG or JPEG")
        if image.width < 256 or image.height < 256:
            raise ValueError("Image width and height must be >= 256")
        if image.width > 1024 or image.height > 1024:
            raise ValueError("Image width and height must be <= 1024")
        self.repository.create(image.filename, image.method, image.psnr, image.ber, image.width, image.height,image.format)
        return image

    def create(self, filename: str, method: str, psnr: float, ber: float, width: float, height: float, format: str) -> bool:
        if not (format == "PNG" or format == "JPEG"):
            raise ValueError("Image format must be PNG or JPEG")
        if width < 256 or height < 256:
            raise ValueError("Image width and height must be >= 256")
        if width > 1024 or height > 1024:
            raise ValueError("Image width and height must be <= 1024")
        self.repository.create(filename, method, psnr, ber, width, height, format)
        return 0



