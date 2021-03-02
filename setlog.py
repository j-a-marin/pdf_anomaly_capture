
import logging                                                                  
import sys                                                                      

class Temp:                                                                     
    def __init__(self, is_verbose=False):                                       
        # configuring log                                                       
        if (is_verbose):                                                        
            self.log_level=logging.DEBUG                                        
        else:                                                                   
            self.log_level=logging.INFO                                         

        log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
        self.log = logging.getLogger(__name__)                                  
        self.log.setLevel(self.log_level)                                       

        # writing to stdout                                                     
        handler = logging.StreamHandler(sys.stdout)                             
        handler.setLevel(self.log_level)                                        
        handler.setFormatter(log_format)                                        
        self.log.addHandler(handler)                                            

        # here                                                                  
        self.log.debug("test")    

def setup_log():

    import logging
    import datetime

    # Get the previous frame in the stack, otherwise it would
    # be this function!!!

    logger = logging.getLogger(__name__)

    if logger.handlers:
       logger.handlers[0].close()
       logger.handlers = []

    datelog = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logHandler = logging.FileHandler(f"DocProcessor_{datelog}.log", mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout) 
    stream_handler.setFormatter(formatter)

    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler) 
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)   

    return logger                                           

if __name__ == "__main__":                                                      
    logger = Temp(True)
