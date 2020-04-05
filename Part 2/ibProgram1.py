# Below are the import statements 

from ibapi.wrapper import *
from ibapi.client import *
from ibapi.contract import *
from ibapi.order import *
from threading import Thread
import queue
import datetime
import time

# Below are the global variables



# Below are the custom classes and methods 

def contractCreate():
    # Fills out the contract object
    contract1 = Contract()  # Creates a contract object from the import
    contract1.symbol = "AAPL"   # Sets the ticker symbol 
    contract1.secType = "STK"   # Defines the security type as stock
    contract1.currency = "USD"  # Currency is US dollars 
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract1.exchange = "SMART"
    # contract1.PrimaryExch = "NYSE"
    return contract1    # Returns the contract object

def orderCreate():
    # Fills out the order object 
    order1 = Order()    # Creates an order object from the import
    order1.action = "BUY"   # Sets the order action to buy
    order1.orderType = "MKT"    # Sets order type to market buy
    order1.transmit = True
    order1.totalQuantity = 10   # Setting a static quantity of 10 
    return order1   # Returns the order object 

def orderExecution():
    #Places the order with the returned contract and order objects 
    contractObject = contractCreate()
    orderObject = orderCreate()
    nextID = 101
    app.placeOrder(nextID, contractObject, orderObject)
    print("order was placed")


# Below is the TestWrapper/EWrapper class

'''Here we will override the methods found inside api files'''

class TestWrapper(EWrapper):

    ## error handling code
    def init_error(self):
        error_queue = queue.Queue()
        self.my_errors_queue = error_queue

    def is_error(self):
        error_exist = not self.my_errors_queue.empty()
        return error_exist

    def get_error(self, timeout=6):
        if self.is_error():
            try:
                return self.my_errors_queue.get(timeout=timeout)
            except queue.Empty:
                return None
        return None

    def error(self, id, errorCode, errorString):
        ## Overrides the native method
        errormessage = "IB returns an error with %d errorcode %d that says %s" % (id, errorCode, errorString)
        self.my_errors_queue.put(errormessage)

    def init_time(self):
        time_queue = queue.Queue()
        self.my_time_queue = time_queue
        return time_queue

    def currentTime(self, server_time):
        ## Overriden method
        self.my_time_queue.put(server_time)


# Below is the TestClient/EClient Class 

'''Here we will call our own methods, not overriding the api methods'''

class TestClient(EClient):

    def __init__(self, wrapper):
    ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

    def server_clock(self):

        print("Asking server for Unix time")     

        # Creates a queue to store the time
        time_storage = self.wrapper.init_time()

        # Sets up a request for unix time from the Eclient
        self.reqCurrentTime()

        #Specifies a max wait time if there is no connection
        max_wait_time = 10

        try:
            requested_time = time_storage.get(timeout = max_wait_time)
        except queue.Empty:
            print("The queue was empty or max time reached")
            requested_time = None

        while self.wrapper.is_error():
          print("Error:")
          print(self.get_error(timeout=5))
          
        return requested_time

# Below is TestApp Class 

class TestApp(TestWrapper, TestClient):
    #Intializes our main classes 
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        #Connects to the server with the ipaddress, portid, and clientId specified in the program execution area
        self.connect(ipaddress, portid, clientid)

        #Initializes the threading
        thread = Thread(target = self.run)
        thread.start()
        setattr(self, "_thread", thread)

        #Starts listening for errors 
        self.init_error()


# Below is the program execution

if __name__ == '__main__':

    print("before start")

    # Specifies that we are on local host with port 7497 (paper trading port number)
    app = TestApp("127.0.0.1", 7497, 0)     

    # A printout to show the program began
    print("The program has begun")

    #assigning the return from our clock method to a variable 
    requested_time = app.server_clock()

    #printing the return from the server
    print("")
    print("This is the current time from the server " )
    print(requested_time)

    #disconnect the app when we are done with this one execution
    # app.disconnect()

# Below is the input area


# Below is the logic processing area


# Calls the order execution function at the end of the program

time.sleep(3)   # Wait three seconds
orderExecution()
 
















