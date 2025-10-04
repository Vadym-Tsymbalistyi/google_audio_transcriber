from drive_client import GoogleDriveClient


def main():
    drive_client = GoogleDriveClient()
    list_files = drive_client.list_audio_files()

    print("\nСписок  файлів :")
    for f in list_files:
        print(f"{f['name']} (id={f['id']})")


if __name__ == "__main__":
    main()
