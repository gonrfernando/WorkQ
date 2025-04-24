def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('startpage','/startpage')
    config.add_route('sign_in', '/sign-in')
    config.add_route('logout', '/logout')
    config.add_route('sign_up', '/sign-up')
    config.add_route('add_user', '/add_user')


