import asyncio
import bisect

def run_server(host, port):
    class EchoServerProtocol(asyncio.Protocol):
        storage = dict()
        def connection_made(self, transport):
            self.transport = transport

        def data_received(self, data):
            message = data.decode()
            print('Data received: {!r}'.format(message))
            try:
                status, payload = message.split(" ", 1)
                payload = payload.strip()
                if status == "put":
                    try:
                        for row in payload.splitlines():
                            key, value, timestamp = row.split()

                            if key not in EchoServerProtocol.storage:
                                EchoServerProtocol.storage[key] = []
                                bisect.insort(EchoServerProtocol.storage[key], ((int(timestamp), float(value))))
                            else:
                                for_add = []
                                cond = True
                                bisect.insort(for_add, ((int(timestamp), float(value))))
                                for i in range(len(EchoServerProtocol.storage[key])):
                                    if EchoServerProtocol.storage[key][i][0] == int(timestamp):
                                        EchoServerProtocol.storage[key][i] = (int(timestamp), float(value))
                                        cond = False
                                if cond == True:
                                    EchoServerProtocol.storage[key] += for_add
                        self.transport.write(b"ok\n\n")
                    except (IndexError, ValueError):
                        self.transport.write(b"error\nwrong command\n\n")

                elif message == "get *\n":
                    # print("get all")
                    new_string = ""
                    for key in EchoServerProtocol.storage.keys():
                        for value in EchoServerProtocol.storage[key]:
                            new_string += f"{key} {value[1]} {value[0]}\n"
                    if new_string == "":
                        self.transport.write(b"ok\n\n")
                    else:
                        to_sending = "ok\n {} \n\n".format(new_string)
                        self.transport.write(bytes(to_sending, "utf-8"))
                
                elif len(payload.split()) != 1:
                    # print("lenght payload:", payload)
                    self.transport.write(b"error\nwrong command\n\n")

                elif "get" in status:
                    if payload not in EchoServerProtocol.storage.keys():
                        self.transport.write(b"ok\n\n")
                    else:
                        new_string = ""
                        for value in EchoServerProtocol.storage[payload]:
                            new_string += f"{payload} {value[1]} {value[0]}\n"
                        to_sending = "ok\n{}\n".format(new_string)
                        self.transport.write(bytes(to_sending, "utf-8")) 
                else:
                    self.transport.write(b"error\nwrong command\n\n")
            except ValueError:
                self.transport.write(b"error\nwrong command\n\n")

            # self.transport.close()
    loop = asyncio.get_event_loop()
    coro = loop.create_server(EchoServerProtocol, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

# run_server("127.0.0.1", 8888)