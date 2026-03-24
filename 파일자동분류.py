from pathlib import Path
import shutil


DOWNLOAD_DIR = Path(r"C:\Users\student\Downloads")

EXTENSION_TO_FOLDER = {
	".jpg": "images",
	".jpeg": "images",
	".csv": "data",
	".xlsx": "data",
	".txt": "docs",
	".doc": "docs",
	".pdf": "docs",
	".zip": "archive",
}


def get_unique_destination(destination: Path) -> Path:
	"""동일한 파일명이 이미 존재하면 (1), (2) ... 형태로 새 이름을 만든다."""
	if not destination.exists():
		return destination

	stem = destination.stem
	suffix = destination.suffix
	parent = destination.parent
	counter = 1

	while True:
		candidate = parent / f"{stem} ({counter}){suffix}"
		if not candidate.exists():
			return candidate
		counter += 1


def organize_downloads(base_dir: Path) -> None:
	if not base_dir.exists() or not base_dir.is_dir():
		raise FileNotFoundError(f"다운로드 폴더를 찾을 수 없습니다: {base_dir}")

	# 필요한 대상 폴더를 먼저 생성
	for folder_name in set(EXTENSION_TO_FOLDER.values()):
		(base_dir / folder_name).mkdir(exist_ok=True)

	moved_count = 0

	for item in base_dir.iterdir():
		if not item.is_file():
			continue

		target_folder = EXTENSION_TO_FOLDER.get(item.suffix.lower())
		if not target_folder:
			continue

		destination = base_dir / target_folder / item.name
		destination = get_unique_destination(destination)
		shutil.move(str(item), str(destination))
		moved_count += 1
		print(f"이동: {item.name} -> {destination}")

	print(f"완료: 총 {moved_count}개 파일 이동")


if __name__ == "__main__":
	organize_downloads(DOWNLOAD_DIR)
