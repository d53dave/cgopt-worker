/*
 * producer.cpp
 *
 *  Created on: Feb 26, 2015
 *      Author: davidsere
 */


#include <spdlog/spdlog.h>
#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>
#include <uuid/uuid.h>
#include <random>
#include <unistd.h>




void generate_work(std::string host, int port);
//
//int main(int argc, char *argv[]) {
//	generate_work("localhost",5555);
//}

void generate_work(std::string host, int port) {

  const std::string endpoint = "tcp://"+host+":"+std::to_string(port).c_str();

//  console->info() << "Client Startup!";

  // initialize the 0MQ context
  zmqpp::context context;

  // generate a push socket
  zmqpp::socket_type type = zmqpp::socket_type::req;
  zmqpp::socket socket (context, type);

  // open the connection
//  console->info() << "Opening connection to " << endpoint << "...";
  socket.connect(endpoint);

  std::uniform_real_distribution<double> unif(0,10000);
  	  std::default_random_engine re;

  while(true){
	  usleep(3000000); //1sec
	  zmqpp::message req_message;
	  // compose a message from a string and a number
//	  cgopt_request request;

	  char uuidBuff[36];
	  uuid_t uuidGenerated;
	  uuid_generate_random(uuidGenerated);
	  uuid_unparse(uuidGenerated, uuidBuff);

//	  request.set_id(uuidBuff);
//	  request.set_type(request.PUT_WORK);

	  for(int i=0;i<10;++i){
//		  request.add_data(unif(re));
	  }

	  //memcpy(fMessage.mutable_samples()->mutable_data(),
      //&dData[0],
      //sizeof(double)*dData.size());

//	  log_proto_array(request.data());

//	  req_message << request.SerializeAsString();
	  socket.send(req_message);

	  //get the ACK
	  zmqpp::message rep_message;
	  std::string serialized_req;

	  socket.receive(rep_message);
	  rep_message >> serialized_req;

//	  cgopt_response response;
//	  response.ParseFromString(serialized_req);
//
//	  assert(request.id() == response.id());
//	  console->info() << "Received " << response.id()<<", "<< response.type() << " for request " << request.id();
//	  if(response.has_error()){
//		  console->info() << "error received: "<<response.error();
//	  }
  }
}

//void log_proto_array(const google::protobuf::RepeatedField<double> & iter) {
//	std::string s;
//	for (auto it = iter.begin(); it != iter.end(); ++it) {
//		s += std::to_string((double)*it);
//		s += ", ";
//	}
//	console->info() << "Repeatedfield: [" << s << "]";
//}


//void debug_request(cgopt_request request) {
//	std::string s;
//	google::protobuf::TextFormat::PrintToString(request, &s);
//	console->info() << "Request " << s;
//}
//
//void debug_response(cgopt_response response) {
//
//	std::string s;
//	google::protobuf::TextFormat::PrintToString(response, &s);
//	console->info() << "Response " << s;
//}
