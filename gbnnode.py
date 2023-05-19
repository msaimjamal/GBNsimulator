from socket import *
import threading
import sys
import time
import string
import pickle
import random


pack_drop = 0
pack_total = 0


class packet:
    def __init__(self, header, data, type):
        self.type = type
        self.header = header
        self.data = data

class GBNProtocol:
    def __init__(self, port, peerport, window, mode, p):
        self.port = port
        self.peerport = peerport
        self.window = window
        self.mode = mode #deterministic or probabilistic
        self.p = p #probability
        self.next_seq_num = 0 #seq number that has not been sent yet
        self.base = 0 #seq number of oldest unack'd packet
        self.buffer = [] #this is send buffer
        if mode == "det":
            self.detcount = 0



    def send(self): #This is to send packets to recvr node
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.bind(('', self.port))

        #This is multithreading to have our node listen as well as send
        listen = threading.Thread(target=self.recv, args= (client_socket, ))
        listen.start()

        while True: #This is the prompt for the user.
            print("node>", end="")
            try:
                temp = input()  # take inputs in the terminal
                input_list = temp.split()
                data = ""
                header = input_list[0]
                if header != "send": #Only accept SEND input
                    raise Exception
                if header == "send":
                    data = temp[5:]
            except KeyboardInterrupt:
                    print("[Summary] " + str(pack_drop) + "/" + str(pack_total) + " packets discarded. Loss rate = " + str(pack_drop/pack_total) + "%")
                    exit()
            except:
                print("[Invalid input.]")
                continue

            c = 0
            while (c < len(data)):
                for x in range (self.window):
                    if c < len(data):
                        myPacket = packet(self.next_seq_num, data[c], "packet")
                        self.buffer.append(myPacket)
                        #print("Sending packet with sequence number:", myPacket.header)
                        #print("Data: ", data[c])
                        self.next_seq_num += 1

                    c = c+1
                for x in self.buffer:
                    packet_bytes = pickle.dumps(x)
                    client_socket.sendto(packet_bytes, ("127.0.0.1", self.peerport))
                    print("[" + str(time.time()) + "] packet " + str(x.header) + " " + str(x.data) + " sent")


    def recv(self, client_socket): #This would be used to receive ACKs or to send ACKs.
        while True:
            #print("Multithreading Begins")
            buf, sender_address = client_socket.recvfrom(4096)
            received_packet = pickle.loads(buf) # to decode the packet sent over the network
            #lines = buf.splitlines()
            #header = lines[0]
            #data = lines[1]
            if received_packet.type == "packet":
                global pack_total
                pack_total = pack_total + 1
                if mode == "det":
                    if self.detcount == self.p * 10:
                        self.detcount = 0
                        print("[" + str(time.time()) + "] packet " + str(received_packet.header) + " " + str(received_packet.data) + " discarded")
                        global pack_drop
                        pack_drop = pack_drop + 1
                        continue
                    else:
                        self.detcount = self.detcount + 1
                elif mode == "prob":
                    if random.random() <= self.p:
                        print("[" + str(time.time()) + "] packet " + str(received_packet.header) + " " + str(received_packet.data) + " discarded")
                        #global pack_drop
                        pack_drop = pack_drop + 1
                        continue
                print("[" + str(time.time()) + "] packet " + str(received_packet.header) + " " + str(received_packet.data) + " received")
                myPacket = packet(received_packet.header, "a", "ack")
                packet_bytes = pickle.dumps(myPacket)
                client_socket.sendto(packet_bytes, ("127.0.0.1", self.peerport))
                print("[" + str(time.time()) + "] ACK " + str(
                    received_packet.header) + " sent, expecting packet " + str(received_packet.header + 1))
            elif received_packet.type == "ack":
                if mode == "det":
                    if self.detcount == self.p * 10:
                        self.detcount = 0
                        print("[" + str(time.time()) + "] ACK " + str(
                            received_packet.header) + " discarded")
                        continue
                    else:
                        self.detcount = self.detcount + 1
                elif mode == "prob":
                    if random.random() <= self.p:
                        print("[" + str(time.time()) + "] ACK " + str(
                            received_packet.header) + " discarded")
                        continue
                print("[" + str(time.time()) + "] ACK " + str(received_packet.header) + " " + " received, window moves to " + str(received_packet.header + 1))
                if received_packet.header - self.base == 1:
                    self.base = self.base + 1


if __name__ == "__main__":
    allowed_modes = ["-p", "-d"]

    try:
        port = sys.argv[1]
        peerport = sys.argv[2]
        window = sys.argv[3]
        mode = sys.argv[4]
        p = sys.argv[5]
        if mode not in allowed_modes:
            raise Exception
    except IndexError:
        print("[Invalid input.]")
        exit()
    except KeyboardInterrupt:
        exit()
    except Exception:
        print("[Invalid input.]")
        exit()


    if mode == '-d':  # deterministically drop packets
        mode = "det"
    elif mode == '-p':  # drop packets with probability p
        mode = "prob"

    protocol = GBNProtocol(int(port), int(peerport), int(window), mode, float(p))
    protocol.send()

