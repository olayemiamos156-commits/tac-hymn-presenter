TAC HYMN PRESENTER — Cloud Build Project

This project is configured so GitHub Actions can compile a Windows standalone EXE in the cloud. You can set it up from your Android phone. You do not need to install Python on your phone.

IMPORTANT
- The project is a hymn presentation app prototype.
- It does NOT contain the full Apostolic Church hymn collection. hymns.json includes a placeholder only.
- The Windows EXE is built by GitHub Actions; it has not been built or tested in this chat environment.
- The first build creates a Windows EXE and includes hymns.json and this README as downloadable artifact files.
- The EXE can run without Python installed. Once downloaded, keep hymns.json in the same folder as the EXE so hymn changes can be saved.

SET UP FROM AN ANDROID PHONE
1. Open https://github.com in your phone browser and sign in or create a free account.
2. Create a new repository. Give it a name such as tac-hymn-presenter. Choose Public or Private, then create it.
3. In the repository, choose Add file → Upload files.
4. Extract this ZIP on your phone first. Upload the project files and folders to the repository root. IMPORTANT: also upload the hidden .github/workflows/build-windows.yml file. If your phone's file picker hides dot-folders, use GitHub's web editor to create the workflow file at:
   .github/workflows/build-windows.yml
   and paste the contents from this package.
5. Commit the uploaded files to the main branch.
6. Open the repository's Actions tab. Select “Build TAC Hymn Presenter for Windows”. If needed, tap “Run workflow”.
7. Wait for the workflow to finish successfully.
8. Open the completed workflow run, find Artifacts, and download “TAC-Hymn-Presenter-Windows”.
9. Extract the downloaded artifact ZIP on your phone and transfer the EXE plus hymns.json to your Windows PC.

GITHUB FILE UPLOAD TIP
The GitHub mobile website may be awkward for uploading folders and hidden files. If it is too difficult on the phone, the simplest alternative is to use a computer once to upload the files, or ask someone you trust to help with that one upload. Do not share your GitHub password.

USING THE APP
- Connect a projector and set Windows display mode to Extend.
- Open TAC Hymn Presenter.exe.
- Click Open Projector and move the projector window to the second display.
- Use F11 for full screen and Left/Right arrows to change verses.
- Add your own hymn lyrics with Add Hymn or import supported JSON/CSV/TXT data.

No guarantee is made that GitHub's mobile interface will expose every workflow control in exactly the same place; the labels can change.
