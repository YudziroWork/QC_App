class BaseReport:
    def generate(self, results: list, stats: dict, output_path: str):
        raise NotImplementedError