module x10 {
    interface Net {
        void sendMsg(string s);
        string showEnvironment();
        string getEnvironment();
        void setActive(string name);
        void setInactive(string name);
        void addModule(string name, string code, string mtype);
        void delModule(string name);
        string getAlarm(string name);
        void setAlarm(string name, string sh, string sm, string eh, string em, bool act);
        string getRule(string name);
        void setRule(string name, string SenState, string selectMod, string Action);
        void delRule(string name, int rule);
        bool isSensor(string name);
        void delModulebyCode(string code);
        void changeNamebyCode(string name, string code);
        void changeName(string newname, string name);
        bool isActivebyCode(string code);
        bool isAtive(string name);
    };
};


