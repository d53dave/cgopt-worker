/*
 * producer.cpp
 *
 *  Created on: Feb 26, 2015
 *      Author: davidsere
 */


#include "spdlog.h"
#include "cgopt.pb.h"
#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>
#include <uuid/uuid.h>
#include <random>

using namespace std;

auto console = spdlog::stdout_logger_mt("console");

void generate_work(string host, int port);

int main(int argc, char *argv[]) {
	generate_work("localhost",5555);
}

void generate_work(string host, int port) {
  const string endpoint = "tcp://"+host+":"+to_string(port).c_str();

  console->info() << "Client Startup!";

  // initialize the 0MQ context
  zmqpp::context context;

  // generate a push socket
  zmqpp::socket_type type = zmqpp::socket_type::push;
  zmqpp::socket socket (context, type);

  // open the connection
  console->info() << "Opening connection to " << endpoint << "...";
  socket.connect(endpoint);

  while(true){
	  zmqpp::message message;
	  // compose a message from a string and a number
	  cgopt_request request;

	  char uuidBuff[36];
	  uuid_t uuidGenerated;
	  uuid_generate_random(uuidGenerated);
	  uuid_unparse(uuidGenerated, uuidBuff);

	  request.set_id(uuidBuff);
	  request.set_type(request.PUT_WORK);

	  uniform_real_distribution<double> unif(0,10000);
	  default_random_engine re;

	  auto r_data = request.data();
	  for(int i=0;i<100;++i){
		  r_data.Add(unif(re));
	  }
	  message << request.SerializeAsString();
	  socket.send(message);
  }
}
