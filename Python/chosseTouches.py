import random

def Touch_Probability(probabilidad=1): #Define la probabilidad de tener el resplandor
    if random.random() < probabilidad/100:
        return True
    else:
        return False

def Tag_Maker(): #Crea de forma aleatoria una etiqueta de habilidad.
    rank = random.randint(1, 5)  # Se excluye el 6
    match rank:
        case 1:
            rank = 1
        case 2:
            rank = 4
        case 3:
            rank = 8
        case 4:
            rank = 12
        case 5:
            if random.randint(1, 5) == 1:
                rank = 18
            else:
                rank = 8
    category = random.randint(1, 10)
    index = random.randint(1, 10)

    return [rank, category, index]

def Tag_Checker(tag, tag_list, pl):
    if tag_list: 
        #print(tag)
        if tag[0] <= pl:
            for tags in tag_list:
                if tag[1] == tags[1] and tag[2] == tags[2]:
                    return False
            return True
    else:
        if tag[0] <= pl:
            return True
            
    return False

def Tag_Module(tag, tag_list, pl): #Hace mas probable que un juegador se vaya por una sola rama de habilidades
    if tag_list:
        last_tag = tag_list[-1]
        x = last_tag[1]
        newTag = [tag[0], x, tag[2]]
        if Tag_Checker(newTag, tag_list, pl) == True:
            return newTag
        else:
            return tag
    else:
        return tag

def Power_Level():
    pl = random.randint(1, 50)
    if pl > 49:
        pl = pl + random.randint(1, 50)
        if pl > 95:
            pl = pl + random.randint(1, 100)
            if pl >= 195:
                pl = pl + random.randint(1,999)
                return pl
        return pl
    return pl

def Conver_Tag(tag_list):
    newtag_list = []
    for tag in tag_list:
        match tag[0]:
            case 1:
                tag[0] = "D"
            case 4:
                tag[0] = "C"
            case 8:
                tag[0] = "B"
            case 12:
                tag[0] = "A"
            case 18:
                tag[0] = "S"
        newtag_list.append(tag)
    return newtag_list

#test
def chosseTouches():
    if Touch_Probability(100) == False:
        return print("No tienes resplandor")
    tag_list=[]
    pl = Power_Level()
    while pl > 0:
        tag = Tag_Maker()
        #print(tag)
        tag = Tag_Module(tag, tag_list, pl)
        #print(tag)
        print(pl)
        if Tag_Checker(tag, tag_list, pl) == True:
            tag_list.append(tag)
            pl -= tag[0]
            
    return print(Conver_Tag(tag_list))

chosseTouches()