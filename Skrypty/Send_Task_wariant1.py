import requests
import time
import subprocess
import asyncio
import re

pattern = r"Got response"
ilosc_przedmiotow = 3   
class robot:
    def __init__(self,nazwa,wolny,parking,wspolrzedne_parkingu):
        self.nazwa = nazwa
        self.wolny = wolny
        self.parking = parking
        self.wspolrzedne_parkingu = wspolrzedne_parkingu
        self.zadanie = None
        self.stan_zadania = 1
        self.state = 1
        self.destination_arrival = None
        self.doObrabiarki = None
        self.odbiorZobrabiarki = False
        self.replan = False
        self.last_completed_request = -1
        self.completed_request = 0
        self.przedmiot_do_obrobki = None
        self.wykonaj_symulacje = None
        self.doObrabiarki2 = None
        self.x = None
        self.y = None
        self.dotarl = True

    def pobierz_dane_robota(self,url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()  # zakładamy, że dane są w formacie JSON
            else:
                print(f"Nie można pobrać danych. Kod odpowiedzi: {response.status_code}")
                self.nazwa = -1
                self.wolny = -1
                self.parking = -1
                self.zadanie = -1
                self.stan_zadania = -1
                self.state = -1
                self.destination_arrival = -1
                self.doObrabiarki = -1
                self.odbiorZobrabiarki = -1
                return None
        except requests.exceptions.RequestException as e:
            print(f"Wystąpił błąd podczas próby pobrania danych: {e}")
            self.nazwa = -1
            self.wolny = -1
            self.parking = -1
            self.zadanie = -1
            self.stan_zadania = -1
            self.state = -1
            self.destination_arrival = -1
            self.doObrabiarki = -1
            self.odbiorZobrabiarki = -1
            return None

    def zaktualizuj_dane_robota(self):
        link ="http://127.0.0.1:22011/open-rmf/rmf_gazebo_fm/status/"
        data = self.pobierz_dane_robota(link)
        for robot in data['data']['all_robots']:
                if self.nazwa == robot['robot_name']:
                    self.state = robot['state']
                    self.destination_arrival = robot['destination_arrival']
                    self.replan = robot['replan']
                    self.last_completed_request = self.completed_request
                    self.completed_request = robot['last_completed_request']
                    self.x = robot['position']['x']
                    self.y = robot['position']['y']
    
    def wykonaj_zadanie(self,trasa,przedmiot=None,symulacja=False,odbior_z_obrabiarki=False,obrabiarka1='',obrabiarka2='',magazynWyj=None,magazynWej=None):
        if self.dotarl:
            if self.stan_zadania == 1:
                self.zadanie = trasa
                self.stan_zadania=2
                self.doObrabiarki1 = obrabiarka1
                self.doObrabiarki2 = obrabiarka2
                self.odbiorZobrabiarki = odbior_z_obrabiarki
                self.przedmiot_do_obrobki = przedmiot
                self.wykonaj_symulacje = symulacja
                self.magazynWyj = magazynWyj
                self.magazynWej = magazynWej
                self.dotarl = False
                if odbior_z_obrabiarki:
                    self.doObrabiarki1.przedmiot = -1
                robot_not_respond = True
                while robot_not_respond:
                    command = (
                        'ros2 run rmf_tasks dispatch_go_to_place -F tinyRobot -R '
                        + self.nazwa
                        + ' -p '+ self.zadanie[0]+' --use_sim_time'
                    )
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                    if re.search(pattern, result.stdout):
                        robot_not_respond = False
                        

                #subprocess.call(command, shell=True)
            elif self.stan_zadania == 2:
                self.dotarl = False
                self.stan_zadania=3
                robot_not_respond = True
                while robot_not_respond:
                    command = (
                                        'ros2 run rmf_tasks dispatch_go_to_place -F tinyRobot -R '
                        + self.nazwa
                        + ' -p '+ self.zadanie[1]+' --use_sim_time'
                    )
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                    if re.search(pattern, result.stdout):
                        robot_not_respond = False

            elif self.stan_zadania == 3:

                if self.odbiorZobrabiarki:
                    self.doObrabiarki1.wolna = True

                if self.wykonaj_symulacje:
                    self.doObrabiarki1.symuluj_prace()
                
                if self.wykonaj_symulacje and self.odbiorZobrabiarki:
                    self.doObrabiarki2.symuluj_prace()
                
                if not self.magazynWyj:
                    if self.odbiorZobrabiarki:
                        self.doObrabiarki2.przedmiot = self.przedmiot_do_obrobki
                    else:
                        self.doObrabiarki1.przedmiot = self.przedmiot_do_obrobki
                else: 
                    self.magazynWyj.zwieksz_ilosc()
                self.dotarl = False
                self.stan_zadania=4
                robot_not_respond = True
                while robot_not_respond:
                    command = (
                                'ros2 run rmf_tasks dispatch_go_to_place -F tinyRobot -R '
                        + self.nazwa
                        + ' -p '+ self.parking+' --use_sim_time'
                    )
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                    if re.search(pattern, result.stdout):
                        robot_not_respond = False

            elif self.stan_zadania == 4:
                self.stan_zadania=1
                self.wolny = True
                self.doObrabiarki1 = None
                self.doObrabiarki2 = None
                self.odbiorZobrabiarki = False
                self.przedmiot_do_obrobki = None
                self.wykonaj_symulacje = False
                self.magazynWyj = None
                self.magazynWej = None
                self.zadanie = None
                self.dotarl = True
        else:
            if self.magazynWej and self.stan_zadania == 2:
                self.czyDotarl(self.magazynWej.wspolrzedne_magazynu)
            if self.magazynWyj and self.stan_zadania == 3:
               self.czyDotarl(self.magazynWyj.wspolrzedne_magazynu)
            if self.doObrabiarki1 and not self.doObrabiarki2 and self.stan_zadania == 3:
               self.czyDotarl(self.doObrabiarki1.wspolrzedne_obrabiarki)
            if self.doObrabiarki1 and self.doObrabiarki2 and self.stan_zadania == 2:
               self.czyDotarl(self.doObrabiarki1.wspolrzedne_obrabiarki)
            if self.doObrabiarki1 and not self.magazynWej and self.stan_zadania == 2:
               self.czyDotarl(self.doObrabiarki1.wspolrzedne_obrabiarki)
            if self.doObrabiarki2 and self.stan_zadania == 3:
                self.czyDotarl(self.doObrabiarki2.wspolrzedne_obrabiarki)
            if self.stan_zadania == 4:
                self.czyDotarl(self.wspolrzedne_parkingu)
            
           
            
    
    def czyDotarl(self,wspolrzedne_docelowe):
        x = self.isclose(self.x,wspolrzedne_docelowe['x'])
        y = self.isclose(self.y,wspolrzedne_docelowe['y'])
        if x and y:
            self.dotarl = True
    
    def isclose(self,x1,x2):
        if x1 < 0:
            x1 = x1*-1
            x2 = x2*-1
        if (x1 <= x2 + 0.05) and (x1 >= x2-0.05):
            return True


class obrabiarka:
    def __init__(self,czas_pracy,wolna,wspolrzedne_obrabiarki):
        self.czas_pracy = czas_pracy
        self.wolna = wolna
        self.wspolrzedne_obrabiarki = wspolrzedne_obrabiarki
        self.przedmiot = 0
        self.obrobka_trwa = False
        self.czas = 0


    def symuluj_prace(self):
        self.obrobka_trwa = True
        self.czas+=1
        if self.czas == self.czas_pracy:
            self.obrobka_trwa = False
            self.czas = 0

    def wezwij_robot(self,robots,trasa_przedmiotu,przedmiot,symulacja,magazynWyjs=None,obrabiarka=None):

            for robot in robots:
                if (robot.state == 1 or robot.state == 0) and robot.destination_arrival==None and robot.wolny==True and self.przedmiot!=-1:
                    self.przedmiot = -1
                    robot.wolny=False
                    if obrabiarka:
                        obrabiarka.wolna = False
                    robot.wykonaj_zadanie(trasa = trasa_przedmiotu,przedmiot = przedmiot,symulacja = symulacja,odbior_z_obrabiarki=True,obrabiarka1 = self, obrabiarka2= obrabiarka,magazynWyj=magazynWyjs)
                    
    
class magazyn:
    def __init__(self,ilosc,trasa,wspolrzedne_magazynu):
        self.ilosc = ilosc
        self.trasa = trasa
        self.wspolrzedne_magazynu=wspolrzedne_magazynu
    
    def zmniejsc_ilosc(self):
        self.ilosc = self.ilosc-1

    def zwieksz_ilosc(self):
            self.ilosc = self.ilosc+1

    def wezwij_robot(self,robots,obrabiarka,przedmiot,symulacja,ilosc):

            for robot in robots:
                if (robot.state == 1 or robot.state == 0) and robot.destination_arrival==None and robot.wolny==True and (self.ilosc + ilosc) == ilosc_przedmiotow:
                    robot.wolny=False
                    obrabiarka.wolna = False
                    self.zmniejsc_ilosc()
                    robot.wykonaj_zadanie(trasa=self.trasa,przedmiot=przedmiot,symulacja=symulacja,odbior_z_obrabiarki=False,obrabiarka1=obrabiarka,magazynWej = self)


                    
TinyRobot1 = robot('TinyRobot1',True,'TinyRobot1_Spawn',{'x':19.0,'y':-15.75})
TinyRobot2 = robot('TinyRobot2',True,'TinyRobot2_Spawn',{'x':15.5,'y':-14.85})
TinyRobot3 = robot('TinyRobot3',True,'TinyRobot3_Spawn',{'x':14.5,'y':-14.85})
TinyRobot4 = robot('TinyRobot4',True,'TinyRobot4_Spawn',{'x':15.0,'y':-11.0})
TinyRobot5 = robot('TinyRobot5',True,'TinyRobot5_Spawn',{'x':14.5,'y':-5.6})
TinyRobot6 = robot('TinyRobot6',True,'TinyRobot6_Spawn',{'x':19,'y':-6.25})
TinyRobot7 = robot('TinyRobot7',True,'TinyRobot7_Spawn',{'x':6.5,'y':-10.1})
TinyRobot8 = robot('TinyRobot8',True,'TinyRobot8_Spawn',{'x':7.0,'y':-15.75})
TinyRobot9 = robot('TinyRobot9',True,'TinyRobot9_Spawn',{'x':11.0,'y':-18.75})
TinyRobot10 = robot('TinyRobot10',True,'TinyRobot10_Spawn',{'x':29.5,'y':-19.6})
Obrabiarka0 = obrabiarka(10,True,{'x':5,'y':-0.5})
Obrabiarka1 = obrabiarka(10,True,{'x':9,'y':-0.5})
Obrabiarka2 = obrabiarka(10,True,{'x':13,'y':-0.5})
Obrabiarka3 = obrabiarka(4,True,{'x':17,'y':-0.5})
Obrabiarka4 = obrabiarka(3,True,{'x':21,'y':-0.5})
Obrabiarka5 = obrabiarka(6,True,{'x':21,'y':-23.5})
Obrabiarka6 = obrabiarka(6,True,{'x':17,'y':-23.5})
Obrabiarka7 = obrabiarka(6,True,{'x':13,'y':-23.5})
Obrabiarka8 = obrabiarka(6,True,{'x':9,'y':-23.5})
Obrabiarka9 = obrabiarka(5,True,{'x':5,'y':-23.5})
Magazyn1wej = magazyn(ilosc_przedmiotow,['MagazynWej1','Obrabiarka0'],{'x':25,'y':-3.5})
Magazyn2wej = magazyn(ilosc_przedmiotow,['MagazynWej2','Obrabiarka1'],{'x':25,'y':-5.35})
Magazyn3wej = magazyn(ilosc_przedmiotow,['MagazynWej3','Obrabiarka3'],{'x':25,'y':-7.75})
Magazyn4wej = magazyn(ilosc_przedmiotow,['MagazynWej4','Obrabiarka9'],{'x':25,'y':-10.1})
Magazyn5wej = magazyn(ilosc_przedmiotow,['MagazynWej5','Obrabiarka7'],{'x':25,'y':-12.5})
Magazyn6wej = magazyn(ilosc_przedmiotow,['MagazynWej6','Obrabiarka8'],{'x':25,'y':-14.85})
Magazyn7wej = magazyn(ilosc_przedmiotow,['MagazynWej7','Obrabiarka2'],{'x':25,'y':-17.25})
Magazyn8wej = magazyn(ilosc_przedmiotow,['MagazynWej8','Obrabiarka4'],{'x':25,'y':-19.6})
Magazyn1wyj = magazyn(0,[],{'x':1,'y':-3.5})
Magazyn2wyj = magazyn(0,[],{'x':1,'y':-7.75})
Magazyn3wyj = magazyn(0,[],{'x':1,'y':-12.5})
Magazyn4wyj = magazyn(0,[],{'x':1,'y':-17.25})
Magazyn5wyj = magazyn(0,[],{'x':1,'y':-3.5})
Magazyn6wyj = magazyn(0,[],{'x':1,'y':-7.75})
Magazyn7wyj = magazyn(0,[],{'x':1,'y':-12.5})
Magazyn8wyj = magazyn(0,[],{'x':1,'y':-17.25})
Przedmiot1 = {1:['Obrabiarka0','Obrabiarka5'],2:['Obrabiarka5','MagazynWyj1'],'indeks':1}
Przedmiot2 = {1:['Obrabiarka1','Obrabiarka2'],2:['Obrabiarka2','MagazynWyj2'],'indeks':2}
Przedmiot3 = {1:['Obrabiarka3','Obrabiarka6'],2:['Obrabiarka6','MagazynWyj3'],'indeks':3}
Przedmiot4 = {1:['Obrabiarka9','Obrabiarka0'],2:['Obrabiarka0','MagazynWyj4'],'indeks':4}
Przedmiot5 = {1:['Obrabiarka7','Obrabiarka3'],2:['Obrabiarka3','MagazynWyj1'],'indeks':5}
Przedmiot6 = {1:['Obrabiarka8','Obrabiarka4'],2:['Obrabiarka4','MagazynWyj2'],'indeks':6}
Przedmiot7 = {1:['Obrabiarka2','Obrabiarka7'],2:['Obrabiarka7','MagazynWyj3'],'indeks':7}
Przedmiot8 = {1:['Obrabiarka4','Obrabiarka1'],2:['Obrabiarka1','MagazynWyj4'],'indeks':8}
while True:
    print('Magazyn1Wej:',Magazyn1wej.ilosc,'Magazyn1Wyj',Magazyn1wyj.ilosc)
    print('Magazyn2Wej:',Magazyn2wej.ilosc,'Magazyn2Wyj',Magazyn2wyj.ilosc)
    print('Magazyn3Wej:',Magazyn3wej.ilosc,'Magazyn3Wyj',Magazyn3wyj.ilosc)
    print('Magazyn4Wej:',Magazyn4wej.ilosc,'Magazyn4Wyj',Magazyn4wyj.ilosc)
    print('Magazyn5Wej:',Magazyn5wej.ilosc,'Magazyn5Wyj',Magazyn5wyj.ilosc)
    print('Magazyn6Wej:',Magazyn6wej.ilosc,'Magazyn6Wyj',Magazyn6wyj.ilosc)
    print('Magazyn7Wej:',Magazyn7wej.ilosc,'Magazyn7Wyj',Magazyn7wyj.ilosc)
    print('Magazyn8Wej:',Magazyn8wej.ilosc,'Magazyn8Wyj',Magazyn8wyj.ilosc)
    Robots = []
    TinyRobot1.zaktualizuj_dane_robota()
    TinyRobot2.zaktualizuj_dane_robota()
    TinyRobot3.zaktualizuj_dane_robota()
    TinyRobot4.zaktualizuj_dane_robota()
    TinyRobot5.zaktualizuj_dane_robota()
    TinyRobot6.zaktualizuj_dane_robota()
    #TinyRobot7.zaktualizuj_dane_robota()
    #TinyRobot8.zaktualizuj_dane_robota()
    #TinyRobot9.zaktualizuj_dane_robota()
    Robots.append(TinyRobot1)
    Robots.append(TinyRobot2)
    Robots.append(TinyRobot3)
    Robots.append(TinyRobot4)
    Robots.append(TinyRobot5)
    Robots.append(TinyRobot6)
    #Robots.append(TinyRobot7)
   # Robots.append(TinyRobot8)
   # Robots.append(TinyRobot9)
    for Robot in Robots:
        if(Robot.wolny == False and (Robot.state == 0 or Robot.state == 1) and Robot.destination_arrival==None and Robot.last_completed_request == Robot.completed_request and Robot.dotarl == True):
            Robot.wykonaj_zadanie([]) 
        if not Robot.dotarl:
            Robot.wykonaj_zadanie([]) 
    
    if(Obrabiarka0.obrobka_trwa == True):
        Obrabiarka0.symuluj_prace()
    if(Obrabiarka1.obrobka_trwa == True):
        Obrabiarka1.symuluj_prace()
    if(Obrabiarka2.obrobka_trwa == True):
        Obrabiarka2.symuluj_prace()
    if(Obrabiarka3.obrobka_trwa == True):
        Obrabiarka3.symuluj_prace()
    if(Obrabiarka4.obrobka_trwa == True):
        Obrabiarka4.symuluj_prace()
    if(Obrabiarka5.obrobka_trwa == True):
        Obrabiarka5.symuluj_prace()
    if(Obrabiarka6.obrobka_trwa == True):
        Obrabiarka6.symuluj_prace()
    if(Obrabiarka7.obrobka_trwa == True):
        Obrabiarka7.symuluj_prace()
    if(Obrabiarka8.obrobka_trwa == True):
        Obrabiarka8.symuluj_prace()                    
    if(Obrabiarka9.obrobka_trwa == True):
        Obrabiarka9.symuluj_prace()
        
#Przedmiot 1
    if(Obrabiarka0.wolna == True and (Magazyn1wej.ilosc + Magazyn1wyj.ilosc) == ilosc_przedmiotow and Magazyn1wej.ilosc != 0):
        Magazyn1wej.wezwij_robot(Robots,Obrabiarka0,Przedmiot1['indeks'],True,Magazyn1wyj.ilosc)
    
    if(Obrabiarka0.obrobka_trwa == False and Obrabiarka0.wolna == False and Obrabiarka0.przedmiot == 1 and Obrabiarka5.wolna==True):
        Obrabiarka0.wezwij_robot(Robots,Przedmiot1[1],Przedmiot1['indeks'],True,obrabiarka = Obrabiarka5)
    
    if(Obrabiarka5.obrobka_trwa == False and Obrabiarka5.wolna == False and Obrabiarka5.przedmiot == 1):
        Obrabiarka5.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot1[2],przedmiot = Przedmiot1['indeks'],symulacja=False,magazynWyjs=Magazyn1wyj)

#Przedmiot 2
    if(Obrabiarka1.wolna == True and (Magazyn2wej.ilosc + Magazyn2wyj.ilosc) == ilosc_przedmiotow and Magazyn2wej.ilosc != 0):
        Magazyn2wej.wezwij_robot(Robots,Obrabiarka1,Przedmiot2['indeks'],True,Magazyn2wyj.ilosc)
    
    if(Obrabiarka1.obrobka_trwa == False and Obrabiarka1.wolna == False and Obrabiarka1.przedmiot == 2 and Obrabiarka2.wolna==True):
        Obrabiarka1.wezwij_robot(Robots,Przedmiot2[1],Przedmiot2['indeks'],True,obrabiarka = Obrabiarka2)
    
    if(Obrabiarka2.obrobka_trwa == False and Obrabiarka2.wolna == False and Obrabiarka2.przedmiot == 2):
        Obrabiarka2.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot2[2],przedmiot = Przedmiot2['indeks'],symulacja=False,magazynWyjs=Magazyn2wyj)

#Przedmiot 3
    if(Obrabiarka3.wolna == True and (Magazyn3wej.ilosc + Magazyn3wyj.ilosc) == ilosc_przedmiotow and Magazyn3wej.ilosc != 0):
        Magazyn3wej.wezwij_robot(Robots,Obrabiarka3,Przedmiot3['indeks'],True,Magazyn3wyj.ilosc)
    
    if(Obrabiarka3.obrobka_trwa == False and Obrabiarka3.wolna == False and Obrabiarka3.przedmiot == 3 and Obrabiarka6.wolna==True):
        Obrabiarka3.wezwij_robot(Robots,Przedmiot3[1],Przedmiot3['indeks'],True,obrabiarka = Obrabiarka6)
    
    if(Obrabiarka6.obrobka_trwa == False and Obrabiarka6.wolna == False and Obrabiarka6.przedmiot == 3):
        Obrabiarka6.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot3[2],przedmiot = Przedmiot3['indeks'],symulacja=False,magazynWyjs=Magazyn3wyj)


#Przedmiot 4
    if(Obrabiarka9.wolna == True and (Magazyn4wej.ilosc + Magazyn4wyj.ilosc) == ilosc_przedmiotow and Magazyn4wej.ilosc != 0):
        Magazyn4wej.wezwij_robot(Robots,Obrabiarka9,Przedmiot4['indeks'],True,Magazyn4wyj.ilosc)
    
    if(Obrabiarka9.obrobka_trwa == False and Obrabiarka9.wolna == False and Obrabiarka9.przedmiot == 4 and Obrabiarka0.wolna==True):
        Obrabiarka9.wezwij_robot(Robots,Przedmiot4[1],Przedmiot4['indeks'],True,obrabiarka = Obrabiarka0)
    
    if(Obrabiarka0.obrobka_trwa == False and Obrabiarka0.wolna == False and Obrabiarka0.przedmiot == 4):
        Obrabiarka0.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot4[2],przedmiot = Przedmiot4['indeks'],symulacja=False,magazynWyjs=Magazyn4wyj)                 

#Przedmiot 5
    if(Obrabiarka7.wolna == True and (Magazyn5wej.ilosc + Magazyn5wyj.ilosc) == ilosc_przedmiotow and Magazyn5wej.ilosc != 0):
        Magazyn5wej.wezwij_robot(Robots,Obrabiarka7,Przedmiot5['indeks'],True,Magazyn5wyj.ilosc)
    
    if(Obrabiarka7.obrobka_trwa == False and Obrabiarka7.wolna == False and Obrabiarka7.przedmiot == 5 and Obrabiarka3.wolna==True):
        Obrabiarka7.wezwij_robot(Robots,Przedmiot5[1],Przedmiot5['indeks'],True,obrabiarka = Obrabiarka3)
    
    if(Obrabiarka3.obrobka_trwa == False and Obrabiarka3.wolna == False and Obrabiarka3.przedmiot == 5):
        Obrabiarka3.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot5[2],przedmiot = Przedmiot5['indeks'],symulacja=False,magazynWyjs=Magazyn5wyj)                 

#Przedmiot 6
    if(Obrabiarka8.wolna == True and (Magazyn6wej.ilosc + Magazyn6wyj.ilosc) == ilosc_przedmiotow and Magazyn6wej.ilosc != 0):
        Magazyn6wej.wezwij_robot(Robots,Obrabiarka8,Przedmiot6['indeks'],True,Magazyn6wyj.ilosc)
    
    if(Obrabiarka8.obrobka_trwa == False and Obrabiarka8.wolna == False and Obrabiarka8.przedmiot == 6 and Obrabiarka4.wolna==True):
        Obrabiarka8.wezwij_robot(Robots,Przedmiot6[1],Przedmiot6['indeks'],True,obrabiarka = Obrabiarka4)
    
    if(Obrabiarka4.obrobka_trwa == False and Obrabiarka4.wolna == False and Obrabiarka4.przedmiot == 6):
        Obrabiarka4.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot6[2],przedmiot = Przedmiot6['indeks'],symulacja=False,magazynWyjs=Magazyn6wyj)                 

#Przedmiot 7
    if(Obrabiarka2.wolna == True and (Magazyn7wej.ilosc + Magazyn7wyj.ilosc) == ilosc_przedmiotow and Magazyn7wej.ilosc != 0):
        Magazyn7wej.wezwij_robot(Robots,Obrabiarka2,Przedmiot7['indeks'],True,Magazyn7wyj.ilosc)
    
    if(Obrabiarka2.obrobka_trwa == False and Obrabiarka2.wolna == False and Obrabiarka2.przedmiot == 7 and Obrabiarka7.wolna==True):
        Obrabiarka2.wezwij_robot(Robots,Przedmiot7[1],Przedmiot7['indeks'],True,obrabiarka = Obrabiarka7)
    
    if(Obrabiarka7.obrobka_trwa == False and Obrabiarka7.wolna == False and Obrabiarka7.przedmiot == 7):
        Obrabiarka7.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot7[2],przedmiot = Przedmiot7['indeks'],symulacja=False,magazynWyjs=Magazyn7wyj)                 

#Przedmiot 8
    if(Obrabiarka4.wolna == True and (Magazyn8wej.ilosc + Magazyn8wyj.ilosc) == ilosc_przedmiotow and Magazyn8wej.ilosc != 0):
        Magazyn8wej.wezwij_robot(Robots,Obrabiarka4,Przedmiot8['indeks'],True,Magazyn8wyj.ilosc)
    
    if(Obrabiarka4.obrobka_trwa == False and Obrabiarka4.wolna == False and Obrabiarka4.przedmiot == 8 and Obrabiarka1.wolna==True):
        Obrabiarka4.wezwij_robot(Robots,Przedmiot8[1],Przedmiot8['indeks'],True,obrabiarka = Obrabiarka1)
    
    if(Obrabiarka1.obrobka_trwa == False and Obrabiarka1.wolna == False and Obrabiarka1.przedmiot == 8):
        Obrabiarka1.wezwij_robot(Robots,trasa_przedmiotu=Przedmiot8[2],przedmiot = Przedmiot8['indeks'],symulacja=False,magazynWyjs=Magazyn8wyj)    

    time.sleep(1)