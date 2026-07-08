import pygame
import math
import random


pygame.init()


screen = pygame.display.set_mode(
    (0,0),
    pygame.FULLSCREEN
)


WIDTH, HEIGHT = screen.get_size()

clock = pygame.time.Clock()



CENTER = (
    WIDTH//2,
    HEIGHT//2
)


RADIUS = min(WIDTH,HEIGHT)//2 - 10



game_paused = False

mode = "normal"





def inside_circle(x,y):

    return math.hypot(
        x-CENTER[0],
        y-CENTER[1]
    ) < RADIUS-30






def create_worm(x,y,team):

    body=[]


    for i in range(45):

        body.append([
            x-i*9,
            y
        ])


    return {

        "body":body,

        "angle":random.random()*6.28,

        "target":random.random()*6.28,


        "energy":100,

        "team":team,


        "dead":False,

        "corpse":False,

        "corpse_parts":45,

        "decay":0,


        "unlimited":False

    }







worms=[]

foods=[]






def create_food():

    while True:


        x=random.randint(
            CENTER[0]-RADIUS,
            CENTER[0]+RADIUS
        )


        y=random.randint(
            CENTER[1]-RADIUS,
            CENTER[1]+RADIUS
        )



        if inside_circle(x,y):


            foods.append({

                "x":x,

                "y":y,

                "size":4

            })


            break






def add_food():


    for i in range(20):

        create_food()





def remove_food():

    foods.clear()
    
# =====================
# الأزرار
# =====================


brown_button = pygame.Rect(
    20,60,150,45
)


black_button = pygame.Rect(
    180,60,150,45
)


doctor_button = pygame.Rect(
    340,60,150,45
)


food_add_button = pygame.Rect(
    500,60,150,45
)


food_remove_button = pygame.Rect(
    660,60,150,45
)


energy_button = pygame.Rect(
    20,115,150,45
)


pause_button = pygame.Rect(
    180,115,150,45
)


start_button = pygame.Rect(
    340,115,150,45
)





selected_worm=None

spawn_team=None

energy_text=""





# =====================
# تحديد الدودة
# =====================


def select_worm(x,y):

    global selected_worm


    selected_worm=None


    closest=999999



    for worm in worms:


        if worm["dead"]:

            continue



        for part in worm["body"]:


            d=math.hypot(

                part[0]-x,

                part[1]-y

            )



            if d<45 and d<closest:


                closest=d

                selected_worm=worm




    return selected_worm






def handle_click(pos):

    global mode
    global spawn_team
    global game_paused



    if brown_button.collidepoint(pos):


        mode="spawn"

        spawn_team="brown"




    elif black_button.collidepoint(pos):


        mode="spawn"

        spawn_team="black"




    elif doctor_button.collidepoint(pos):


        mode="spawn"

        spawn_team="doctor"




    elif food_add_button.collidepoint(pos):


        add_food()




    elif food_remove_button.collidepoint(pos):


        remove_food()




    elif pause_button.collidepoint(pos):


        game_paused=True




    elif start_button.collidepoint(pos):


        game_paused=False




    elif energy_button.collidepoint(pos):


        if selected_worm is not None:


            mode="energy"


        return






    elif mode=="spawn":


        if inside_circle(

            pos[0],

            pos[1]

        ):


            worms.append(

                create_worm(

                    pos[0],

                    pos[1],

                    spawn_team

                )

            )



        mode="normal"

        spawn_team=None





    else:


        select_worm(

            pos[0],

            pos[1]

        )
        
def kill_worm(worm):

    worm["dead"]=True

    worm["corpse"]=True

    worm["corpse_parts"]=len(
        worm["body"]
    )

    worm["decay"]=0







def update_worms():


    if game_paused:

        return




    for worm in worms:



        if worm["dead"]:


            worm["decay"] += 0.001


            if worm["decay"] > 1:

                worm["decay"]=1


            continue





        head=worm["body"][0]





        # =====================
        # الطبيب
        # =====================


        if worm["team"]=="doctor":



            target=None

            closest=999999



            for other in worms:



                if other==worm:

                    continue



                if other["dead"]:

                    continue



                if other["energy"]>=100:

                    continue




                d=math.hypot(

                    other["body"][0][0]-head[0],

                    other["body"][0][1]-head[1]

                )



                if d<closest:


                    closest=d

                    target=other





            if target:



                worm["target"]=math.atan2(

                    target["body"][0][1]-head[1],

                    target["body"][0][0]-head[0]

                )




                if closest<100:


                    target["energy"]=min(

                        100,

                        target["energy"]+0.2

                    )









        # =====================
        # القتال
        # =====================


        else:



            for enemy in worms:



                if enemy==worm:

                    continue



                if enemy["dead"]:

                    continue



                if enemy["team"]=="doctor":

                    continue



                if enemy["team"]!=worm["team"]:



                    eh=enemy["body"][0]



                    distance=math.hypot(

                        eh[0]-head[0],

                        eh[1]-head[1]

                    )




                    if distance<500:



                        worm["target"]=math.atan2(

                            eh[1]-head[1],

                            eh[0]-head[0]

                        )





                    if distance<25:


                        enemy["energy"]-=0.2



                        if enemy["energy"]<=0:


                            kill_worm(enemy)









        # =====================
        # حركة الرأس
        # =====================


        diff=worm["target"]-worm["angle"]



        worm["angle"]+=diff*0.04




        head[0]+=math.cos(

            worm["angle"]

        )*1.7



        head[1]+=math.sin(

            worm["angle"]

        )*1.7






        # الجسم يتبع الرأس


        for i in range(1,len(worm["body"])):


            before=worm["body"][i-1]

            part=worm["body"][i]



            dx=before[0]-part[0]

            dy=before[1]-part[1]



            dist=math.hypot(dx,dy)



            if dist>9:


                part[0]+=dx*0.25

                part[1]+=dy*0.25
                
        # =====================
        # البحث عن جثة عند الجوع
        # =====================


        if worm["energy"] < 30 and not worm["unlimited"]:


            nearest=None

            closest=999999



            for dead in worms:


                if dead["corpse"] and dead["corpse_parts"]>0:


                    d=math.hypot(

                        dead["body"][0][0]-head[0],

                        dead["body"][0][1]-head[1]

                    )


                    if d<closest:


                        closest=d

                        nearest=dead






            if nearest:



                worm["target"]=math.atan2(

                    nearest["body"][0][1]-head[1],

                    nearest["body"][0][0]-head[0]

                )





                if closest<20:



                    nearest["corpse_parts"]-=1



                    worm["energy"]=min(

                        100,

                        worm["energy"]+2

                    )



                    if len(nearest["body"])>1:


                        nearest["body"].pop()



                    if nearest["corpse_parts"]<=0:


                        nearest["corpse"]=False








        # =====================
        # منع الخروج من الحدود
        # =====================


        dx=head[0]-CENTER[0]

        dy=head[1]-CENTER[1]


        dist=math.hypot(dx,dy)




        if dist>RADIUS-35:



            head[0]=CENTER[0]+dx/dist*(RADIUS-35)

            head[1]=CENTER[1]+dy/dist*(RADIUS-35)



            worm["angle"]=math.atan2(

                CENTER[1]-head[1],

                CENTER[0]-head[0]

            )


            worm["target"]=worm["angle"]







        # =====================
        # نقصان الطاقة
        # =====================


        if not worm["unlimited"]:


            worm["energy"]-=0.01




        if worm["energy"]<=0:


            kill_worm(worm)








        # =====================
        # أكل الغذاء
        # =====================


        for food in foods[:]:


            if math.hypot(

                food["x"]-head[0],

                food["y"]-head[1]

            )<15:



                foods.remove(food)



                worm["energy"]=min(

                    100,

                    worm["energy"]+30

                )
                
# =====================
# لوحة الأرقام
# =====================


numbers=[

"1","2","3",

"4","5","6",

"7","8","9",

"DEL","0","OK"

]



keys=[]



for i,key in enumerate(numbers):


    keys.append((

        key,

        pygame.Rect(

            WIDTH//2-150+(i%3)*100,

            HEIGHT//2+50+(i//3)*70,

            80,

            55

        )

    ))







def handle_energy_click(pos):


    global mode

    global energy_text



    if selected_worm is None:


        mode="normal"

        return






    for key,rect in keys:



        if rect.collidepoint(pos):



            if key=="OK":


                try:



                    value=float(

                        energy_text

                    )



                    selected_worm["energy"]=value




                    # 100 أو أكثر = طاقة لا نهائية


                    if value>=100:


                        selected_worm["unlimited"]=True



                    else:


                        selected_worm["unlimited"]=False




                except:


                    pass




                energy_text=""

                mode="normal"






            elif key=="DEL":



                energy_text=energy_text[:-1]






            else:



                energy_text+=key
                
font = pygame.font.SysFont(
    None,
    28
)




running=True



while running:


    for event in pygame.event.get():


        if event.type==pygame.QUIT:

            running=False




        if event.type==pygame.MOUSEBUTTONDOWN:


            if mode=="energy":


                handle_energy_click(
                    event.pos
                )


            else:


                handle_click(
                    event.pos
                )






    update_worms()






    screen.fill(
        (8,10,12)
    )





    pygame.draw.circle(

        screen,

        (210,230,215),

        CENTER,

        RADIUS

    )







    # الغذاء


    for food in foods:


        pygame.draw.circle(

            screen,

            (80,180,80),

            (
                int(food["x"]),
                int(food["y"])
            ),

            food["size"]

        )






    # الديدان


    for worm in worms:



        if worm["dead"]:


            color=(80,180,80)



        elif worm["team"]=="brown":


            color=(150,100,70)



        elif worm["team"]=="black":


            color=(10,10,10)



        else:


            color=(0,120,255)






        for x,y in worm["body"]:


            pygame.draw.circle(

                screen,

                color,

                (
                    int(x),
                    int(y)
                ),

                8

            )






        # تحديد الدودة وإظهار المعلومات


        if worm==selected_worm:



            pygame.draw.circle(

                screen,

                (255,255,0),

                (
                    int(worm["body"][0][0]),
                    int(worm["body"][0][1])
                ),

                15,

                3

            )



            energy_info=font.render(

                "Energy: "+str(int(worm["energy"])),

                True,

                (255,255,255)

            )


            team_info=font.render(

                "Team: "+worm["team"],

                True,

                (255,255,255)

            )



            screen.blit(

                energy_info,

                (
                    int(worm["body"][0][0])-60,
                    int(worm["body"][0][1])-70
                )

            )



            screen.blit(

                team_info,

                (
                    int(worm["body"][0][0])-60,
                    int(worm["body"][0][1])-40
                )

            )







    # رسم الأزرار


    buttons=[


        (brown_button,"Brown"),


        (black_button,"Black"),


        (doctor_button,"Doctor"),


        (food_add_button,"Food+"),


        (food_remove_button,"Food-"),


        (energy_button,"Energy"),


        (pause_button,"Pause"),


        (start_button,"Start")

    ]





    for rect,text in buttons:


        pygame.draw.rect(

            screen,

            (70,70,70),

            rect

        )



        screen.blit(

            font.render(

                text,

                True,

                (255,255,255)

            ),

            (
                rect.x+5,
                rect.y+10
            )

        )






    # لوحة تعديل الطاقة


    if mode=="energy":



        pygame.draw.rect(

            screen,

            (230,230,230),

            (
                WIDTH//2-170,
                HEIGHT//2-120,
                340,
                430
            )

        )



        for key,rect in keys:


            pygame.draw.rect(

                screen,

                (70,70,70),

                rect

            )


            screen.blit(

                font.render(

                    key,

                    True,

                    (255,255,255)

                ),

                (
                    rect.x+20,
                    rect.y+15
                )

            )



        screen.blit(

            font.render(

                energy_text,

                True,

                (0,0,0)

            ),

            (
                WIDTH//2-40,
                HEIGHT//2-90
            )

        )







    pygame.display.flip()


    clock.tick(60)



pygame.quit()