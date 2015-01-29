if __name__ == '__main__':
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser
    from importlib import import_module
    import os, os.path
    import subprocess

    def is_valid_filepath(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg
    
    # argument parsing
    parser = ArgumentParser()
    parser.add_argument('config', type=lambda x: is_valid_filepath(parser, x),
        help="Configuration file path")
    parser.add_argument('--no-browser', dest='browser', action='store_false')
    args = parser.parse_args()

    # load in the configuration file
    config = ConfigParser({
        'certfile' : None,
        'keyfile' : None,
        'ca_certs' : None,
        'ssl' : False,
        'port' : '8{0:03d}',
        'icons': 'link',
        'corpus_link' : None,
        'doc_title_format' : None,
        'doc_url_format' : None,
        'topic_range': None,
        'topics': None})
    config.read(args.config)

    if config.get('main', 'topic_range'):
        topic_range = map(int, config.get('main', 'topic_range').split(','))
        topic_range = range(*topic_range)
    if config.get('main', 'topics'):
        topic_range = eval(config.get('main', 'topics'))

    procs = [subprocess.Popen("python server.py -k %d %s" % (k, args.config),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        preexec_fn=os.setsid) for k in topic_range]

    print "pid","port"
    for proc,k in zip(procs, topic_range):
        port = config.get("main","port").format(k)
        print proc.pid, "http://localhost:{0}/".format(port)

    import signal,sys
    def signal_handler(sig,frame):
        print "\n"
        for p in procs:
            print "killing", p.pid
            os.killpg(p.pid, signal.SIGINT)
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    import urllib, webbrowser
    import time
    port = config.get("main","port").format(topic_range[0])
    url = "http://localhost:{0}/".format(port)

    while True:
        try:
            urllib.urlopen(url)
            print "Server successfully started"
            break
        except:
            time.sleep(1)
    if args.browser:
        webbrowser.open(url)

    print "Press Ctrl+C to shutdown the Topic Explorer server"
    signal.pause()