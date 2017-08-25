//
// Created by dotdi on 20.11.16.
//

#include "MessageQueueClient.h"

namespace CSAOpt{
void MessageQueue::runPlumbingRepReqLoop(std::string host, unsigned int port) {
    this->logger->info("Entering Plumbing REP/REQ loop");

    memberMap members;

    zmqpp::context context;

    const zmqpp::socket_type type = zmqpp::socket_type::rep;
    zmqpp::socket socket{context, type};

    const zmqpp::endpoint_t endpoint = fmt::format("tcp://{}:{}", host, port);
    this->logger->info("Binding plumbing socket on {}", endpoint.c_str());
    socket.bind(endpoint);

    zmqpp::poller poller;
    poller.add(socket);

    while (this->run) {
        if (poller.poll(100)) {
            logger->info("Plumbing rep/req loop pass");
            zmqpp::message req;
            socket.receive(req);
            auto begin = std::chrono::high_resolution_clock::now();

            logger->info("Plumbing rep/req loop recv message");
            std::string strBuf;
            req >> strBuf;

            kj::std::StringPipe pipe(strBuf);
            ::capnp::PackedMessageReader recvMessage(pipe);

            this->logger->info("Plumbing rep/req loop message deserialized");

            Plumbing::Reader recvPlumbing = recvMessage.getRoot<Plumbing>();

            this->logger->info("Received plumbing with Id {}", recvPlumbing.getId().cStr());


            ::capnp::MallocMessageBuilder message;
            Plumbing::Builder plumbing = message.initRoot<Plumbing>();

            plumbing.setId(recvPlumbing.getId());
            plumbing.setTimestamp(time_t(0));

            switch (recvPlumbing.getType()) {
                case Plumbing::Type::REGISTER:
                    handleRegister(plumbing, recvPlumbing, members);
                    break;
                case Plumbing::Type::UNREGISTER:
                    handleUnregister(plumbing, recvPlumbing, members);
                    break;
                case Plumbing::Type::HEARTBEAT:
                    handleHeartbeat(plumbing, recvPlumbing, members);
                    break;
                case Plumbing::Type::STATS:
                    handleStats(plumbing, members);
                    break;
                default:
                    logger->warn("Unrecognized Message type: {}", (uint16_t) recvPlumbing.getType());
                    break;
            }

            kj::std::StringPipe pipe2;
            writePackedMessage(pipe2, message);

            logger->info("Sending response for plumbing with id {}", plumbing.getId().cStr());

            zmqpp::message resp;
            resp << pipe2.getData();

            socket.send(resp);
            logger->debug("Response for plumbing with id {} sent", plumbing.getId().cStr());
            auto end = std::chrono::high_resolution_clock::now();
            auto responseTime = std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();
            saveResponseTime(responseTime);
            logger->debug("Response time for plumbing with id {} was {}ms", plumbing.getId().cStr(), responseTime);
        }
    }
//        workQueue = {};
    members.clear();
}
}