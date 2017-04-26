module x10 {
    interface Net {
        void sendMsg(string s);
        string showEnvironment();
        string getEnvironment();
        void setActive(string name);
        void setInactive(string name);
        void addModule(string name, string code, string mtype);
        void delModule(string name);
        bool isSensor(string name);
        bool isCode(string code);
        void delModulebyCode(string code);
        void changeNamebyCode(string name, string code);
        void changeName(string newname, string name);
        bool isActivebyCode(string code);
        bool isActive(string name);
    };
};


