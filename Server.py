import numpy as np
from concurrent import futures
import grpc
import greet_pb2
import greet_pb2_grpc

file_path = 'server_weight.txt'  # Path to weights file
def read_weights_from_file(file_path):
    weights_list = []
    with open(file_path, 'r') as file:
        for line in file:
            weights_array = np.fromstring(line.strip(), dtype=float, sep=',')
            weights_list.append(weights_array.reshape(5, 5))  # Assuming weights are in shape (5, 5)
    return weights_list
def federated_averaging(weights_list):
    # Initialize aggregated weights with zeros
    aggregated_weights = np.zeros_like(weights_list[0])
    
    # Aggregate weights from all clients
    for weights in weights_list:
        aggregated_weights += weights
    
    # Calculate average of aggregated weights
    avg_weights = aggregated_weights / len(weights_list)
    
    return avg_weights
class GreeterServicer(greet_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        print("InteractingHello Request Made:")
        print(request.weights)
        # Convert repeated field to a comma-separated string
        weights_str = ','.join(map(str, request.weights))
        # Create and write to a file
        with open("server_weight.txt", "a") as file:
            file.write(weights_str + '\n')

        # Store received weights
        #self.weights_list.append(np.array(request.weights).reshape(5, 5))
                
        # Calculate average weights
        average_weights = federated_averaging(read_weights_from_file('server_weight.txt'))
        print("average weights") 
        print(average_weights)        
        # Create reply
        hello_reply = greet_pb2.HelloReply()
        hello_reply.message = f"{request.greeting} {request.name}"
        hello_reply.weights.extend(average_weights.flatten())  # Flatten the weights
            
        return hello_reply
    
    def InteractingHello(self, request_iterator, context):
        for request in request_iterator:
            print("InteractingHello Request Made:")
            #print(request.weights)
            # Convert repeated field to a comma-separated string
            weights_str = ','.join(map(str, request.weights))
            # Create and write to a file
            with open("server_weight.txt", "a") as file:
                file.write(weights_str + '\n')
    
            # Store received weights
            #self.weights_list.append(np.array(request.weights).reshape(5, 5))
                    
            # Calculate average weights
            average_weights = federated_averaging(read_weights_from_file('server_weight.txt'))
            print("average weights") 
            print(average_weights)        
            # Create reply
            hello_reply = greet_pb2.HelloReply()
            hello_reply.message = f"{request.greeting} {request.name}"
            hello_reply.weights.extend(average_weights.flatten())  # Flatten the weights
                
            yield hello_reply
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) # If this goes more than num of max_workers,we will have some problem!
    greeter_servicer = GreeterServicer()
    greet_pb2_grpc.add_GreeterServicer_to_server(greeter_servicer, server)
    server.add_insecure_port("localhost:50051")
    server.start()
    print("Server started. Listening on port 50051...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        print("Server stopped.")

if __name__ == "__main__":
    serve()
