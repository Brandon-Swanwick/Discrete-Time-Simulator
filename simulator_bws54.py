import math
import os
import random
import sys

class CPU:
    def __init__(self):
        self.clock = 0
        self.idle = True
        self.Process = Process()

class Process:
    def __init__(self):
        self.arrivalTime = 0
        self.serviceTime = 0
        self.startTime = 0
        self.completionTime = 0
        self.Rvalue = 0
        self.remainingServiceTime = 0

class Event:
    def __init__(self):
        self.actionTime = 0
        # 0 is arrival
        # 1 is departure
        # 2 (needs another quantum)
        self.actionType = 0
        self.Process = Process()

class Simulator:
    def __init__(self, scheduleType, givenLambda, avgServiceTime, quantum):
        # parameters for simulator
        self.cpu = CPU()
        self.scheduleType = scheduleType
        self.givenLambda = givenLambda
        self.avgServiceTime = avgServiceTime
        self.quantum = quantum

        # end conditions and result counters
        self.endCondition = 10000
        self.completedProcessCount = 0
        self.totalTurnaroundTime = 0
        self.totalServiceTime = 0
        self.readyQueueProcessCount = 0

        # queues
        self.readyQueue = []
        self.eventQueue = []

    def FCFS(self):

        self.Initialize()

        while self.completedProcessCount != self.endCondition:
            
            # sorting event queue based on time in increasing order
            self.eventQueue.sort(key=lambda i: i.actionTime)

            # handeling next event based on time
            currentEvent = self.eventQueue.pop(0)

            # jumping cpu clock to time of the next event
            self.cpu.clock = currentEvent.actionTime

            # determining what type of event has arrived
            # event is a arrival
            if currentEvent.actionType == 0:

                # if the arrival occurs during when the cpu is not busy
                if self.cpu.idle == True:

                    # updating cpu state to busy, then scheduling the next departure
                    self.cpu.idle = False
                    currentEvent.actionType = 1
                    currentEvent.Process.completionTime = self.cpu.clock + currentEvent.Process.serviceTime
                    currentEvent.actionTime = currentEvent.Process.completionTime

                    # finish scheduling the next departure and add it do eventQueue
                    self.eventQueue.append(currentEvent)

                # if the arrival occurs when the cpu is busy, then add it to the readyQueue
                else:
                    self.readyQueue.append(currentEvent.Process)

                # create a new process and attach it to an arrival event
                newProcess = self.generateProcess()
                nextEvent = self.generateEvent(0, newProcess.arrivalTime, newProcess)
                self.eventQueue.append(nextEvent)

            # event is a departure
            else:

                # updating variables
                self.completedProcessCount += 1
                self.readyQueueProcessCount += len(self.readyQueue)
                self.totalTurnaroundTime += (self.cpu.clock - currentEvent.Process.arrivalTime)
                self.totalServiceTime += currentEvent.Process.serviceTime

                # if the readyQueue is empty set the cpu status to idle
                if len(self.readyQueue) == 0:
                    self.cpu.idle = True

                # if the ready queue is not empty schedule the next departure based on the process pulled from readyQueue
                else:
                    newProcess = self.readyQueue.pop(0)
                    newProcess.startTime = self.cpu.clock
                    newProcess.completionTime = newProcess.startTime + newProcess.serviceTime
                    newEvent = self.generateEvent(1, newProcess.completionTime, newProcess)
                    self.eventQueue.append(newEvent)

    def SRTF(self):

        self.Initialize()

        while self.completedProcessCount != self.endCondition:

            # sorting event queue based on time in increasing order
            self.eventQueue.sort(key=lambda i: i.actionTime)

            # handeling next event based on time
            currentEvent = self.eventQueue.pop(0)

            # jumping cpu clock to time of the next event
            self.cpu.clock = currentEvent.actionTime

            # determining what type of event has arrived
            # event is a arrival
            if currentEvent.actionType == 0:

                # if the arrival occurs during when the cpu is not busy
                if self.cpu.idle == True:

                    # updating cpu state to busy, then scheduling the next departure
                    self.cpu.idle = False
                    currentEvent.actionType = 1
                    currentEvent.Process.completionTime = self.cpu.clock + currentEvent.Process.remainingServiceTime
                    currentEvent.actionTime = currentEvent.Process.completionTime

                    # finish scheduling the next departure and add it do eventQueue   
                    self.eventQueue.append(currentEvent)

                    # set the current process in the CPU
                    self.cpu.Process = currentEvent.Process

                # if the arrival occurs when the cpu is busy then calculate the process with the shortest remaining time to completion
                else:
                    self.readyQueue.append(currentEvent.Process)

                    # find the process with the shortest remaining time in the readyQueue
                    self.readyQueue.sort(key=lambda i: i.remainingServiceTime)

                    # find out the remaining service time of process currently on CPU
                    self.cpu.Process.remainingServiceTime = self.cpu.Process.completionTime - self.cpu.clock

                    # if the readyQueue isnt empty and the current process has a remaining time that is greater than the smallest
                    # remaining time in the readyQueue, switch the two processes
                    if len(self.readyQueue) != 0:
                        if self.cpu.Process.remainingServiceTime > self.readyQueue[0].remainingServiceTime:

                            # find the departure event matched with the current process in the CPU and get rid of it
                            for i in range(len(self.eventQueue)):
                                if self.eventQueue[i].Process == self.cpu.Process:
                                    self.eventQueue.pop(i)

                            # put the current process back in the readyQueue and create a new departure event for that process
                            self.readyQueue.append(self.cpu.Process)
                            new_event = self.generateEvent(1, (self.cpu.clock + self.readyQueue[0].remainingServiceTime), self.readyQueue.pop(0))
                            self.eventQueue.append(new_event)

                            # set the current process in the CPU to the one in the readyQueue with the SRT left
                            self.cpu.Process = new_event.Process
                        else:
                            # if current process on CPU has shorter remaining time do nothing since it will need to finish first
                            pass
                    else:
                        # if ready queue is empty do nothing
                        pass

                # create a new process and attach it to an arrival event
                newProcess = self.generateProcess()
                nextEvent = self.generateEvent(0, newProcess.arrivalTime, newProcess)
                self.eventQueue.append(nextEvent)

            else:

                # updating variables
                self.completedProcessCount += 1
                self.readyQueueProcessCount += len(self.readyQueue)
                self.totalTurnaroundTime += (self.cpu.clock - currentEvent.Process.arrivalTime)
                self.totalServiceTime += currentEvent.Process.serviceTime
                self.cpu.Process = None

                # if the readyQueue is empty set the cpu status to idle
                if len(self.readyQueue) == 0:
                    self.cpu.idle = True

                # if the readyQueue isnt empty find the event with the shortest remaing service time and schedule it in
                # the events as a departure and in the current CPU process
                else:
                    self.readyQueue.sort(key=lambda i: i.remainingServiceTime)
                    newProcess = self.readyQueue.pop(0)
                    newProcess.startTime = self.cpu.clock
                    newProcess.completionTime = newProcess.startTime + newProcess.remainingServiceTime
                    self.cpu.Process = newProcess
                    newEvent = self.generateEvent(1, newProcess.completionTime, newProcess)
                    self.eventQueue.append(newEvent)

    def HRRN(self):

        self.Initialize()

        while self.completedProcessCount != self.endCondition:

            # sorting event queue based on time in increasing order
            self.eventQueue.sort(key=lambda i: i.actionTime)

            # handeling next event based on time
            currentEvent = self.eventQueue.pop(0)

            # jumping cpu clock to time of the next event
            self.cpu.clock = currentEvent.actionTime

            # determining what type of event has arrived
            # event is a arrival
            if currentEvent.actionType == 0:

                # if the arrival occurs during when the cpu is not busy
                if self.cpu.idle == True:

                    # updating cpu state to busy, then scheduling the next departure
                    self.cpu.idle = False
                    currentEvent.actionType = 1
                    currentEvent.Process.completionTime = self.cpu.clock + currentEvent.Process.serviceTime
                    currentEvent.actionTime = currentEvent.Process.completionTime
                    self.eventQueue.append(currentEvent)

                # if the CPU is busy add the process to the readyQueue
                else:
                    self.readyQueue.append(currentEvent.Process)

                # create a new process and put it in an arrival event in the eventQueue
                newProcess = self.generateProcess()
                nextEvent = self.generateEvent(0, newProcess.arrivalTime, newProcess)
                self.eventQueue.append(nextEvent)

            else:

                # updating variables
                self.completedProcessCount += 1
                self.readyQueueProcessCount += len(self.readyQueue)
                self.totalTurnaroundTime += (self.cpu.clock - currentEvent.Process.arrivalTime)
                self.totalServiceTime += currentEvent.Process.serviceTime
                
                # if the readyQueue is empty the cpu goes idle
                if len(self.readyQueue) == 0:
                    self.cpu.idle = True

                # if ready queue is not empty, calculate response ratio and choose the highest one
                else:
                    for i in range(len(self.readyQueue)):
                        self.readyQueue[i].Rvalue = ((self.cpu.clock - self.readyQueue[i].arrivalTime) + self.readyQueue[i].serviceTime) / self.readyQueue[i].serviceTime

                    self.readyQueue.sort(key=lambda i: i.Rvalue, reverse=True)
                    newProcess = self.readyQueue.pop(0)
                    newProcess.startTime = self.cpu.clock
                    newProcess.completionTime = newProcess.startTime + newProcess.serviceTime

                    # attach the process to a departure event
                    newEvent = self.generateEvent(1, newProcess.completionTime, newProcess)
                    self.eventQueue.append(newEvent)

    def RR(self):
        
        self.Initialize()

        while self.completedProcessCount != self.endCondition:

            # sorting event queue based on time in increasing order
            self.eventQueue.sort(key=lambda i: i.actionTime)

            # handeling next event based on time
            currentEvent = self.eventQueue.pop(0)

            # jumping cpu clock to time of the next event
            self.cpu.clock = currentEvent.actionTime
            currentEvent.Process.startTime = self.cpu.clock

            # event is a arrival
            if currentEvent.actionType == 0:

                # if the CPU is idle, make it busy
                if self.cpu.idle == True:
                    self.cpu.idle = False

                    # if process needs more than one quantum to finish create a reschedule event
                    if currentEvent.Process.remainingServiceTime > self.quantum:
                        currentEvent.actionType = 2
                        currentEvent.actionTime = self.cpu.clock + self.quantum
                        currentEvent.Process.remainingServiceTime -= self.quantum

                    # if the process can finish in a quantum or less schedule a departure event
                    else:
                        self.completedProcessCount += 1
                        self.readyQueueProcessCount += len(self.readyQueue)
                        self.totalTurnaroundTime += (self.cpu.clock - currentEvent.Process.arrivalTime)
                        self.totalServiceTime += currentEvent.Process.serviceTime

                        currentEvent.actionType = 1
                        currentEvent.Process.completionTime = self.cpu.clock + currentEvent.Process.remainingServiceTime
                        currentEvent.actionTime = currentEvent.Process.completionTime

                    # put the process in the CPU current process and event in the eventQueue
                    self.cpu.Process = currentEvent.Process
                    self.eventQueue.append(currentEvent)

                # if the CPU is busy put the event in the readyQueue
                else:
                    self.readyQueue.append(currentEvent.Process)

                # create a new process and attach it to an arrival event
                newProcess = self.generateProcess()
                nextEvent = self.generateEvent(0, newProcess.arrivalTime, newProcess)
                self.eventQueue.append(nextEvent)

            # event is a reschedule
            elif currentEvent.actionType == 2:

                # if the readyQueue is empty
                if len(self.readyQueue) == 0:

                    # if process needs more than one quantum to finish reduce the remaining service time and put back in eventQueue
                    if currentEvent.Process.remainingServiceTime > self.quantum:
                        currentEvent.Process.remainingServiceTime -= self.quantum
                        currentEvent.actionTime += self.quantum
                        self.eventQueue.append(currentEvent)

                    # if the process can finish in under or equal to a quantum schedule a departure event
                    else:
                        currentEvent.actionType = 1
                        currentEvent.actionTime = currentEvent.Process.remainingServiceTime + self.cpu.clock
                        self.eventQueue.append(currentEvent)

                # if the readyQueue has processes in it
                else:

                    # put the current process in the back of the readyQueue and get the next process in the readyQueue
                    self.readyQueue.append(self.cpu.Process)
                    nextProces = self.readyQueue.pop()

                    # if the process form the front of the readyQueue can finish in one quantum or less schedule a departure event
                    if nextProces.remainingServiceTime <= self.quantum:

                        # schedule a departure event
                        nextEvent = self.generateEvent(1, (self.cpu.clock + currentEvent.Process.remainingServiceTime), nextProces)
                        nextEvent.Process.completionTime = nextEvent.actionTime
                        self.cpu.Process = nextEvent.Process
                        self.cpu.Process.startTime = self.cpu.clock
                        self.eventQueue.append(nextEvent)

                    # if the process can't finish in a quantum
                    else:

                        # schedule another reschedule
                        nextEvent = self.generateEvent(2, (self.cpu.clock + self.quantum), nextProces)
                        nextEvent.Process.remainingServiceTime -= self.quantum
                        self.cpu.Process = nextEvent.Process
                        self.cpu.Process.startTime = self.cpu.clock
                        self.eventQueue.append(nextEvent)

            # event is a departure
            else:

                # updating variables
                self.completedProcessCount += 1
                self.readyQueueProcessCount += len(self.readyQueue)
                self.totalTurnaroundTime += (self.cpu.clock - currentEvent.Process.arrivalTime)
                self.totalServiceTime += currentEvent.Process.serviceTime

                # if the readyQueue is empty, make the cpu idle
                if len(self.readyQueue) == 0:
                    self.cpu.idle = True

                # if the ready queue is not empty
                else:

                    # take the next process from the ready queue
                    nextProces = self.readyQueue.pop(0)

                    # if the process can finish in under a quantum
                    if nextProces.remainingServiceTime <= self.quantum:

                        # schedule a departure event
                        nextEvent = self.generateEvent(1, (self.cpu.clock + currentEvent.Process.remainingServiceTime), nextProces)
                        nextEvent.Process.completionTime = nextEvent.actionTime
                        self.cpu.Process = nextEvent.Process
                        self.cpu.Process.startTime = self.cpu.clock
                        self.eventQueue.append(nextEvent)

                    # if the process needs more than one quantum to finish
                    else:
                        # schedule another reschedule
                        nextEvent = self.generateEvent(2, (self.cpu.clock + self.quantum), nextProces)
                        nextEvent.Process.remainingServiceTime -= self.quantum
                        self.cpu.Process = nextEvent.Process
                        self.cpu.Process.startTime = self.cpu.clock
                        self.eventQueue.append(nextEvent)

    def driver(self):
        if self.scheduleType == 1:
            self.FCFS()
        elif self.scheduleType == 2:
            self.SRTF()
        elif self.scheduleType == 3:
            self.HRRN()
        elif self.scheduleType == 4:
            self.RR()
        else:
            print("scheduleType not recognized")
            exit(-1)

    def writeToFile(self):

        if self.scheduleType == 1:
            label = "FCFS"
        elif self.scheduleType == 2:
            label = "SRTF"
        elif self.scheduleType == 3:
            label = "HRRN"
        elif self.scheduleType == 4:
            label = "RR"
        else:
            print("scheduleType not recognized")

        avgTT = round((self.totalTurnaroundTime / self.endCondition), 3)
        throughput = round((self.endCondition / self.cpu.clock), 3)
        utilization = round((self.totalServiceTime / self.cpu.clock), 3)
        avgreadyQcount = round(self.readyQueueProcessCount / (self.endCondition), 3)

        if os.path.exists("simData.txt") == False:
            # file is empty (doesn't exist) so write header then info
            with open("simData.txt", "w") as sim_data:
                sim_data.write("Scheduler\tLambda\t AvgServiceTime\t  AvgTurnaroundTime\tThroughput\tCPU Util\tAvg#ProcReadyQ\t   Quantum\n")
                sim_data.write( "----------------------------------------------------------------------------------------------------------------------------\n")
                sim_data.write(label + "\t\t ")                
                sim_data.write(str(self.givenLambda) + "\t\t")
                sim_data.write(str(self.avgServiceTime) + "\t\t")
                sim_data.write(str(avgTT) + "\t\t  ")
                sim_data.write(str(throughput) + "\t   ")
                sim_data.write(str(utilization) + "\t\t")
                sim_data.write(str(avgreadyQcount) + "\t\t")
                sim_data.write(str(self.quantum) + "\n")
                sim_data.close()
        else:
            # file is NOT empty do not write header info only append info
            with open("simData.txt", "a") as sim_data:
                sim_data.write(label + "\t\t ")                
                sim_data.write(str(self.givenLambda) + "\t\t")
                sim_data.write(str(self.avgServiceTime) + "\t\t")
                sim_data.write(str(avgTT) + "\t\t  ")
                sim_data.write(str(throughput) + "\t   ")
                sim_data.write(str(utilization) + "\t\t")
                sim_data.write(str(avgreadyQcount) + "\t\t")
                sim_data.write(str(self.quantum) + "\n")
                sim_data.close()
        print("\nResults have been written to simData.txt in current directory")
        print("\nFormatting of result file may vary based on system\n")
    
    def Initialize(self):
        firstProcess = self.generateProcess()
        firstEvent = self.generateEvent(0, firstProcess.arrivalTime, firstProcess)
        self.eventQueue.append(firstEvent)

    def generateArrivalTime(self):
        arrivalTime = self.cpu.clock + (math.log(self.genRand()) *  (-1/self.givenLambda))
        return arrivalTime

    def genRand(self):
        randNum = 0.0
        randNum = float(random.uniform(0,1))
        return randNum

    def generateServiceTime(self):
        serviceTime = math.log(self.genRand()) * (-1 * self.avgServiceTime)
        return serviceTime

    def generateEvent(self, actionType, actionTime, process):
        newEvent = Event()
        newEvent.actionType = actionType
        newEvent.actionTime = actionTime
        newEvent.Process = process

        return newEvent

    def generateProcess(self):
        newProcess = Process()
        newProcess.arrivalTime = self.generateArrivalTime()
        newProcess.serviceTime = self.generateServiceTime()
        newProcess.startTime = 0
        newProcess.completionTime = newProcess.arrivalTime + newProcess.serviceTime
        newProcess.remainingServiceTime = newProcess.serviceTime

        return newProcess

def main():
    if len(sys.argv) == 5:
        scheduleType = int(sys.argv[1])
        givenLambda = int(sys.argv[2])
        avgServiceTime = float(sys.argv[3])
        quantum = float(sys.argv[4])

        sim = Simulator(scheduleType, givenLambda, avgServiceTime, quantum)
        sim.driver()
        sim.writeToFile()
    else:
        print("please enter arguments as follows \nfilename: \nscheudleType(1: FCFS, 2: SRTF, 3: HRRN, 4: RR): \nlambdaValue: \navgServiceTime: \nQuantumValue(enter 0 if not testing RR: Otherwise do NOT enter 0 for RR testing or program will hang)\n\nExample:: python3 simulator_bws54.py 1 10 0.04 0")

if __name__=="__main__":
    main()  