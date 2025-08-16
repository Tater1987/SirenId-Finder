# SirenId-Finder for FiveM
Just an ai written python script to search your directory for vehicles with carcol.meta files and extract the sirenIds. Will search for duplicates and output everything to a .txt file.

Place inside your main resource folder and right click inside the directory and open in terminal.

Once terminal is open type python carcols_extractor.py and hit enter.

The python script will run in terminal or powershell and set results in 2 .txt files.

One will be a simplified .txt containing all the sirenIDs in your server.

The other will be a list of duplicates vehicles with the same sirenID numbers and what folder they are in.

If you have one folder of vehicle files in your resources change line 9:

self.base_directories = ["emergency"]

to the folder name you need to search. Mine is labeled [emergency] so that is what I used.

Likewise if you have multiple folders in your resources you would like to check use line 211:

 directories_to_search = [ #if you have multiple vehilce folders put them here as they are typed in your resource folder.
    "[emergency]",
    "[Vehicles]",
]
And change or add as needed for the folders you have.

If you see anything that can be approved on submit a PR.
