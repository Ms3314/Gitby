import argparse
import json
from pathlib import Path
import sys 
# this is an parsing library used to pass in parametress 

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
        
        self.index_file.write_text(json.dumps({},indent=2))

        print(f"Initialized an empty git repository in {self.git_dir}")
        return True 


def main():
    parser = argparse.ArgumentParser(
        description= "Gitby , my git alternative"
    )
    subparser = parser.add_subparsers(
        dest="command",
        # basically all the command u give after pythob main.py will be stored in this global var
        help = "Available commands"
    )

    # init_parser = subparser.add_parser("init" , help="initialze a new repository")
    # argss1 = subparser.add_parser("cheche",help="help function")
    argss2 = subparser.add_parser("init",help="init function")
    # temp = parser.parse_args();
    args = parser.parse_args();
    # print(args , args.command);
    
    if not args.command:
        parser.print_help();
        return ;

    try:
        if args.command == "init":
            repo = Repository();
            if not repo.init():
                print("Repository has already been init")
                return 
    except Exception as e :
        print(f"Error : {e}")
        sys.exit(1);



main()

