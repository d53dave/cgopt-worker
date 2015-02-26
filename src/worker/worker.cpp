#include "spdlog.h"
#include "cgopt.pb.h"
#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>
#include <uuid/uuid.h>
#include <random>

using namespace std;

void process_work(string host, int port);

auto console = spdlog::stdout_logger_mt("console");

int main(int argc, char *argv[]) {
	process_work("localhost", 5555);
}

void process_work(string host, int port) {
	const string endpoint = "tcp://" + host + ":" + to_string(port).c_str();

	console->info() << "Client Startup!";

	// initialize the 0MQ context
	zmqpp::context context;

	// generate a push socket
	zmqpp::socket_type type = zmqpp::socket_type::push;
	zmqpp::socket socket(context, type);

	// open the connection
	console->info() << "Opening connection to " << endpoint << "...";
	socket.connect(endpoint);

	while (true) {
		zmqpp::message req;
		// compose a message from a string and a number
		cgopt_request request;
		request.set_id("0");
		request.set_type(request.GET_WORK);

		req << request.SerializeAsString();
		socket.send(req);
		console->info() << "Sent request";

		req.reset_read_cursor();
		console->info() << "Getting response response";
		socket.receive(req);

		console->info() << "Received response";

		string serialized_res;

		req >> serialized_res;

		cgopt_response cgresp;
		cgresp.ParseFromString(serialized_res);

		auto a = cgresp.data();

		double sum = std::accumulate(a.begin(), a.end(), 0.0);
		double mean = sum / a.size();

		double sq_sum = std::inner_product(a.begin(), a.end(), a.begin(), 0.0);
		double stdev = std::sqrt(sq_sum / a.size() - mean * mean);

		console->info() << "ID="<< cgresp.id() <<"\nData Avg="<<mean<<" StDev="<<stdev;
	}

}
