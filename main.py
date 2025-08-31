import argparse
import json
from pathlib import Path
import sys 
import hashlib
import zlib

# this is an parsing library used to pass in parametress 

class GitObject: 
    def __init__(self , obj_type:str , content:bytes):
        self.type = obj_type ;
        self.content = content ;
    def hash(self):
        # we make a mixture od type + size + the content as the hash 
        header = (f"{self.type} {len(self.content)}\0").encode() ;
        return hashlib.sha1(header + self.content).hexdigest();

    def serialization(self):
        #we need to do a losslesss compression on the the particular hash that i s created 
        header = (f"{self.type} {len(self.content)}\0").encode() ;
        return zlib.compress(header + self.content);

    #this methood is used to convert the serialized blog back to the hash format 
    @classmethod
    def deserialization(cls , data:bytes) -> "GitObject":
        decompressed = zlib.decompress(data);
        null_index = decompressed.find(b"\0");
        header = decompressed[:null_index];
        content = decompressed[null_index+1:];
        # obj_type = decompressed[:decompressed.find(" ")];
        # obj_len = decompressed[decompressed.find(" ")+1 :];
        obj_type , size = header.split(" ");
        return cls(obj_type , content);


class Blob(GitObject):
    def __init__ (self , content:bytes):
        super().__init__("blob" , content)
    def get_content(self) -> bytes :
        return self.content 
    


class Repository: 
    def __init__(self , path = "."):
        self.path = Path(path).resolve()
        self.git_dir = self.path / ".gitby"  

        # .git/objects 
        self.objects_dir = self.git_dir / "objects"
        
        # .git/refs
        self.refs_dir = self.git_dir / "refs"
        self.head_dir = self.refs_dir / "heads" 
        # Head files
        self.head_file = self.git_dir / "HEAD"

        # .git/index
        self.index_file = self.git_dir / "index"

    def init(self) -> bool:
        print(self.git_dir)
        if self.git_dir.exists():
            return False 
        

        # create directories here 
        self.git_dir.mkdir()
        self.objects_dir.mkdir()
        self.refs_dir.mkdir()
        self.head_dir.mkdir()

        # create a head file that points to 
        # this refs point to the heads and the main active branch so u can name it anything 

        self.head_file.write_text("ref: refs/heads/master\n")
        
        self.save_index({})
        print(f"Initialized an empty git repository in {self.git_dir}")
        return True 
    
    # this is the standard starting point for adding a path or a directory 
    def add_path(self , path:str) -> None: 
        full_path = self.path / path ;
        if not full_path.exists:
            raise FileNotFoundError(f"Path {full_path} not found") ; 
        if full_path.is_file():
            self.add_file(path);
        elif full_path.is_dir():
            self.add_directory(path);
        else :
            raise ValueError(f"{path} is neither a file or a directory")
    
    # this function is used to store the object path onto the fs 
    def store_object(self , obj:GitObject) :
        # i am getting the object here thu which i can call certain methood
        obj_hash = obj.hash();
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]
        
        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True);
            obj_file.write_bytes(obj.serialization())
        return obj_hash ;

    def load_index(self ) -> dict[str , str]:
        if not self.index_file.exists():
            return {}
        
        try: 
            return json.loads(self.index_file.read_text())
        except:
            return {}

    # this is used to save the content in the index file     
    def save_index(self , index: dict[str , str]):
        self.index_file.write_text(json.dumps(index , indent=2))

    # this is used to add a specific file 
    def add_file(self , path : str)  :
        full_path = self.path / path ;
        if not full_path.exists():
            raise FileNotFoundError(f"Path {full_path} not found");
        # reading the file content 
        content = full_path.read_bytes();
        # create a blob object
        blob = Blob(content);
        # store the blob object in the database (.git/objects)
        blob_hash = self.store_object(blob); 
        # update the index to index the file to this particular hash 
        index = self.load_index()
        index[path] = blob_hash ;
        self.save_index(index);

        print(f"Added {path}")

    def add_directory(self , path:str):
        full_path = self.path / path ;
        if not full_path.exists():
            raise FileNotFoundError(f"Directory {full_path} not found");
        if not full_path.is_dir():
            raise ValueError(f"{path} is not a directory");
        # we need to recursively traverse the directories 
        index = self.load_index()
        added_count = 0 ;
        notneeded = [".gitby" , ".git"];
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if any(part in notneeded for part in file_path.parts):
                    continue ;
             # create and store blob object
                content = file_path.read_bytes() ;
                blob = Blob(content);
                blob_hash = self.store_object(blob);
                # update the index to index the file to this particular hash 
                rel_path = str(file_path.relative_to(self.path))
                index[rel_path] = blob_hash ;
                added_count += 1 ;

            
        self.save_index(index);
        if added_count > 0 :
            print(f"Added {added_count} files from directory {path}");
        else :
            print(f"Directory path already upto date")
        # create blob objects for all files 
        # store all the blobs in the objects db ()
        #update all index to include all the files 
        
        

            

            


def main():
    parser = argparse.ArgumentParser(
        description= "Gitby , my git alternative"
    )
    subparser = parser.add_subparsers(
        dest="command",
        # basically all the command u give after pythob main.py will be stored in this global var
        help = "Available commands"
    )


    init_parser = subparser.add_parser("init",help="init function")
    # add command
    add_parser = subparser.add_parser("add" , help = "add files and Directories to the staging area ")
    
    add_parser.add_argument("paths",nargs='+' , help="Files and directories to add");
    
    args = parser.parse_args();

    #this provides the command that is being executed
    # print(args , args.command);
    
    if not args.command:
        parser.print_help();
        return ;

    repo = Repository();
    try:
        if args.command == "init":
            if not repo.init():
                print("Repository has already been init")
                return 
        if args.command == "add":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return 
            for path in args.paths:
                repo.add_path(path);
                
    except Exception as e :
        print(f"Error : {e}")
        sys.exit(1);



main()

