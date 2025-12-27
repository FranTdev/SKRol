import chosseTouches


def Program():
    if chosseTouches.Touch_Probability(1) == True:
        Level = chosseTouches.Power_Level()
        print(f"Tu nivel de poder es: {Level}")
        Tags_List = []

        while Level > 0:
            # print(f"LV {Level}")
            if Level == 1:
                break
            Tag = chosseTouches.Tag_Generator()
            # print(Tag)
            if chosseTouches.Tag_Check_PL(Level, Tag) == True:
                if chosseTouches.Tag_Check_Repeat(Tags_List, Tag) == True:
                    Level = chosseTouches.Mod_Level(Level, Tag)
                    chosseTouches.Tag_Add(Tags_List, Tag)
                    # print("Tag guardado")

        print("----Tus Habilidades Son:----")
        for tag in Tags_List:
            print(tag)
    else:
        print("No tienes el toque")


Program()
