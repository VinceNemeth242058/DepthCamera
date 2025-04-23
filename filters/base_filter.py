class BaseFilter:
    def apply(self, frame, landmarks, image_shape):
        """Override in subclasses to apply effect."""
        raise NotImplementedError("Filter must implement apply() method.")