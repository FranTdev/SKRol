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
            if random.randint(1, 10) == 1:
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
    if pl >= 45:
        pl = pl + random.randint(1, 50)
        if pl >= 95:
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

def Order_Tags(tag_list):
    """
    Ordena las etiquetas primero por Categoría (tag[1]) 
    y luego por Index (tag[2]).
    """
    if len(tag_list) > 1:
        medio = len(tag_list) // 2
        izquierda = tag_list[:medio]
        derecha = tag_list[medio:]

        # Llamadas recursivas
        Order_Tags(izquierda)
        Order_Tags(derecha)

        i = j = k = 0

        while i < len(izquierda) and j < len(derecha):
            # Lógica de comparación:
            # 1. ¿La categoría de la izquierda es menor?
            # 2. ¿Son iguales pero el index de la izquierda es menor?
            if (izquierda[i][1] < derecha[j][1]) or \
               (izquierda[i][1] == derecha[j][1] and izquierda[i][2] < derecha[j][2]):
                tag_list[k] = izquierda[i]
                i += 1
            else:
                tag_list[k] = derecha[j]
                j += 1
            k += 1

        # Limpieza de elementos restantes
        while i < len(izquierda):
            tag_list[k] = izquierda[i]
            i += 1
            k += 1

        while j < len(derecha):
            tag_list[k] = derecha[j]
            j += 1
            k += 1
            
    return tag_list

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
    tag_list = Order_Tags(tag_list)

    return print(Conver_Tag(tag_list))



chosseTouches()
