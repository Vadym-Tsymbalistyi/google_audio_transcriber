from drive_client import GoogleDriveClient


def main():
    drive_client = GoogleDriveClient()
    copied_files = drive_client.copy_to_workspace_folder()
    print("\nList of copied files in the work folder Drive:")
    for f in copied_files:
        print(f"{f['name']} (id={f['id']})")


if __name__ == "__main__":
    main()
