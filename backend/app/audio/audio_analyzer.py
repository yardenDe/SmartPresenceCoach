import opensmile


class AudioAnalyzer:
    def __init__(
        self,
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.Functionals,
    ):
        self.smile = opensmile.Smile(
            feature_set=feature_set,
            feature_level=feature_level,
        )

    def analyze(self, file_path: str) -> dict:
        features = self.smile.process_file(file_path)

        return features.iloc[0].to_dict()