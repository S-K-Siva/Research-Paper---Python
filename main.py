import math as m
import random
tot_nodes = 200
tot_radius = 100
tot_angle = 360

#source_node_id = 1 (change)
class Package:
    def __init__(self,distance):
        self.k = 2048
        self.d = distance
        self.E_elec = 50 * m.pow(10,-9)
        self.E_amp = 100 * m.pow(10,-12)
        self.data = ""


class Node(Package):
    def __init__(self,radius,teta,id):
        super().__init__(0)
        self.R = radius
        self.teta = teta
        self.id = id
        self.power = 0.5
        self.x = self.R * m.cos(self.teta)
        self.y = self.R * m.sin(self.teta)
        self.package = Package((self.x,self.y))
        self.neighbours = []
        self.neighbours_id = []
        self.received_packets_cnt = 0

    def power_reduction(self,d):
        e_tx = self.package.E_elec * self.k + self.package.E_amp * self.k * m.pow(d,2)
        print("Power reduction......................................",e_tx)

        self.power -= e_tx
        return self.power

    def print_info(self):
        print(f"\t\t\t\tDATA OF {self.id}")
        print(f"\t\t\tNode power is {self.power}")

class Main(Node):
    packets_cancel = 0
    def __init__(self,radius,teta,id):
        super().__init__(radius,teta,id)
        self.base_station = Node(radius,teta,id)
        self.base_station.package.data = None
        self.users = []

    def get_nodes(self):
        for i in range(0,tot_nodes):
            new_radius = random.randint(0,tot_radius)
            new_angle = random.randint(0,tot_angle)
            new_node = Node(new_radius,new_angle,(i+1))
            self.users.append(new_node)

    def get_neighbours(self):
        for i in range(0,len(self.users)):
            base_d = m.sqrt(pow(self.users[i].x - self.base_station.x,2)+pow(self.users[i].y - self.base_station.y,2))
            if base_d <= 72:
                self.base_station.neighbours.append(self.users[i])
                self.base_station.neighbours_id.append(self.users[i].id)
            for j in range(0,len(self.users)):
                if i == j:
                    continue
                else:
                    d = m.sqrt(pow(self.users[i].x - self.users[j].x,2)+pow(self.users[i].y - self.users[j].y,2))
                    if d <= 72:
                        self.users[i].neighbours.append(self.users[j])
                        self.users[i].neighbours_id.append(self.users[j].id)

    def isolated_nodes(self):
        isolated = []
        for node in self.users:
            if len(node.neighbours_id) == 0:
                isolated.append(node)

        print("The isolated nodes are...")
        if len(isolated) == 0:
            print("None")
        else:
            for i in isolated:
                print(i.id)


    def print_all_data(self):
        print("{}:({},{}),co-ordinates:({:.2f},{:.2f})".format(self.base_station.id,self.base_station.R,self.base_station.teta,self.base_station.x,self.base_station.y))
        print("{}:".format(self.base_station.id),self.base_station.neighbours_id)
        for node in self.users:
            print("{}:({},{}),co-ordinates:({:.2f},{:.2f})".format(node.id,node.R,node.teta,node.x,node.y))
            print("{}:".format(node.id),node.neighbours_id)

    def distance(self,point1):
        return m.sqrt(m.pow(point1.x,2)+m.pow(point1.y,2))

    '''
    Sending package by it's energy need to be solved.
    to-do:
        change formula
        track the received packets and cancelled packets of the base station.
        channel analysis (d,d2,d4) --> need to be taught by mam.
    '''
    def send_package(self):
        pack_cnt = 0
        for node in self.users:
            for _ in range(100):
                pack_cnt += 1
                print("Pack_cnt:",pack_cnt)
                if node: #change done here instead of if node == source_node_id
                    #create a package data
                    node.package.data = "Hello base_station"
                    #check whether the node is isolated node or not
                    if len(node.neighbours) == 0:
                        self.packets_cancel += 1
                        print("The node is isolated node!")
                        continue
                    #check if node's neighbours has base_station,if it is there ,send package
                    elif self.base_station.id in node.neighbours_id:
                        self.base_station.package.data = node.package.data
                        self.received_packets_cnt += 1
                        print("the package sent to the base station successfully from {} node".format(node.id))
                        print("The package received from source to base station is ", self.base_station.package.data)
                        continue
                    #check whether the neighbours node distance is low than the current node and send pack
                    else:
                        current = node
                        while True:
                            print("The package of the node {} is ".format(current.id), current.package.data)
                            if len(current.neighbours_id) == 0:
                                self.packets_cancel += 1
                                print("\nThe package couldn't sent !!\n")
                                break
                            else:
                                N = []
                                for new_node in current.neighbours:
                                    if self.distance(new_node) <= self.distance(current):
                                        N.append(new_node)
                                if len(N) == 0:
                                    self.packets_cancel += 1
                                    print("\nThe package couldn't sent!!!!\n")
                                    break

                                smallest_node = N[0]
                                for item in N:
                                    if item.id <= N[0].id:
                                        smallest_node = item
                                if self.distance(smallest_node) < self.distance(current):
                                    smallest_node.package.data = current.package.data
                                    print("\t\t\t\tDistance of both nodes")
                                    print("\t\t\tThe current node distance:",self.distance(current))
                                    print("\t\t\tThe dest node distance:",self.distance(smallest_node))
                                    print("The package sent to {} node from {} node".format(smallest_node.id,current.id))

                                    if self.distance(smallest_node) == 0.0:
                                        self.base_station.package.data = smallest_node.package.data
                                        self.received_packets_cnt += 1
                                        print("\nThe package sent to the base station form {} node successfully\n".format(smallest_node.id))
                                        break
                                    di = m.sqrt(m.pow(current.x - smallest_node.x,2)+m.pow(current.y - smallest_node.y,2))
                                    if current.power <= 0:
                                        self.packets_cancel += 1
                                        print("\nThe {} node's battery dead!,couldn't send package!\n".format(current.id))
                                        break
                                    print("\n\t\tBefore sending package\n.....")
                                    print("\tCurrent node :")
                                    current.print_info()
                                    print("\tDest node :")
                                    smallest_node.print_info()
                                    current.power = current.power_reduction(di)
                                    print("\n\t\tAfter sending package.....")
                                    print("\tCurrent node :")
                                    current.print_info()
                                    print("\tDest node :")
                                    smallest_node.print_info()
                                    current.package.data = smallest_node.package.data
                                    current = smallest_node

                                else:
                                    self.packets_cancel += 1
                                    print("The package couldn't sent allast!",self.distance(smallest_node),self.distance(current))
                                    break



            else:
                continue




if __name__ == "__main__":
    board = Main(0,0,-1)
    board.get_nodes()
    board.get_neighbours()
    board.print_all_data()
    board.isolated_nodes()
    board.send_package()
    print("Packets accepted:",board.received_packets_cnt)
    print("Cancelled packets:",board.packets_cancel)
    print(50 * m.pow(10,-9))
    if(50 * m.pow(10,-9) < 1):
        print("Yes")
    else:
        print("No")

    print("Basement of the protocol completed successfully")


