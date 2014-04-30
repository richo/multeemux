use std::os;
use std::io::net::ip::SocketAddr;
use std::io::net::tcp::TcpStream;
use std::io::net::unix::UnixStream;

fn tmux_socket() -> UnixStream {
    let socket_path = os::getenv("TMUX").unwrap();
    match UnixStream::connect(&socket_path.as_slice()) {
        Ok(s) => s,
        Err(e) => fail!("Couldn't connect to tmux: {}", e)
    }
}

fn usage() {
    let args = os::args();
    println!("Usage: {} [--listen] | [-connect HOST:PORT]", args[0]);
    os::set_exit_status(1);
}

fn listen() {
    println!("LISTEN");
}

fn connect(hostspec: &str) {
    let addr: SocketAddr = match from_str(hostspec) {
        Some(h) => h,
        None => fail!("Couldn't parse address: {}", hostspec)
    };
    let mut socket = match TcpStream::connect(addr) {
        Ok(s) => s,
        Err(e) => fail!("Couldn't connect: {}: {}", addr, e)
    };

    let tmux = tmux_socket();

    spawn(proc() {
        println!("Proxy code goes here");

    });

    println!("sleeping forever");
    std::io::timer::sleep(5);
}

fn main() {
    let args = os::args();

    if args.len() == 2 && args[1].eq(&("--listen".to_owned())) {
        return listen();
    }

    if args.len() == 3 && args[1].eq(&("--connect".to_owned())) {
        return connect(args[2]);
    }

    usage();
}
