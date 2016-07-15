#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>
#include <uuid/uuid.h>
#include <random>
#include <unistd.h>
#include <spdlog/spdlog.h>

void process_work(std::string host, int port);

auto console = spdlog::stdout_logger_mt("console");

int main(int argc, char *argv[]) {
	process_work("localhost", 5555);
}

void process_work(std::string host, int port) {
	const std::string endpoint = "tcp://" + host + ":" + std::to_string(port).c_str();

	console->info() << "Client Startup!";

	// initialize the 0MQ context
	zmqpp::context context;

	// generate a push socket
	zmqpp::socket_type type = zmqpp::socket_type::req;
	zmqpp::socket socket(context, type);

	// open the connection
	console->info() << "Opening connection to " << endpoint << "...";
	socket.connect(endpoint);

	while (true) {
		usleep(2000000); //1sec
		zmqpp::message req;
		// compose a message from a string and a number
//		cgopt_request request;
//		request.set_id("0");
//		request.set_type(request.GET_WORK);
//
//		req << request.SerializeAsString();
//		socket.send(req);
//		console->info() << "Sent request";
//
//		req.reset_read_cursor();
//		console->info() << "Getting response response";
//		socket.receive(req);
//
//		console->info() << "Received response";
//
//		std::string serialized_res;
//
//		req >> serialized_res;
//
//		cgopt_response cgresp;
//		cgresp.ParseFromString(serialized_res);
//
//		//assert(request.id() != cgresp.id());
//		if (cgresp.type() == cgresp.WORK && !cgresp.has_error()) {
//			auto a = cgresp.data();
//
//			log_proto_array(cgresp.data());
//
//			double sum = std::accumulate(a.begin(), a.end(), 0.0);
//			double mean = sum / a.size();
//
//			double sq_sum = std::inner_product(a.begin(), a.end(), a.begin(),
//					0.0);
//			double stdev = std::sqrt(sq_sum / a.size() - mean * mean);
//
//			console->info() << "ID=" << cgresp.id() << "\nData Avg=" << mean
//					<< " StDev=" << stdev;
//		} else {
//			console->warn() << "Response " << cgresp.id() << " has error "
//					<< cgresp.error();
//		}
//
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
