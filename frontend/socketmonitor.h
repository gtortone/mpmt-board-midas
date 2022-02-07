#include "zmq.hpp"

class socketMonitor : public zmq::monitor_t {
public:
    // listening for the on_event_connected event, notify user if successful. 
    void on_event_connected(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_CONNECTED;
        eventName = "Connected";
    }

    void on_event_accepted(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_ACCEPTED;
        eventName = "Accepted";
    }

    void on_event_disconnected(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_DISCONNECTED;
        eventName = "Disconnected";
    }

    void on_event_connect_retried(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_CONNECT_RETRIED;
        eventName = "Connection Retired";
    }

    void on_event_listening(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_LISTENING;
        eventName = "Listening";
    }

    void on_event_connect_delayed(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_CONNECT_DELAYED;
        eventName = "Connect Delayed";
    }

    void on_event_accept_failed(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_ACCEPT_FAILED;
        eventName = "Accept Failed";
    }

    void on_event_closed(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_CLOSED;
        eventName = "Closed";
    }

    void on_event_bind_failed(const zmq_event_t& event, const char* addr) override {
        eventID = ZMQ_EVENT_BIND_FAILED;
        eventName = "Bind Failed";
    }

    int eventID;
    std::string eventName;
};
