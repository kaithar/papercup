import hashlib
import traceback
from tornado import gen
import tornado.autoreload
import logging

from papercup import config

class NestedException(Exception):
    pass

def exception_catcher(func, self, *args, **kwargs):
    try:
        return func(self, *args, **kwargs)
    except:
        ex = traceback.format_exc()
        raise NestedException(ex)

def use_template(template_file, filename=None, use_thread=False):
    def template_wrapper(function_to_wrap):
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger('papercup.templating')
            try:
                content = None
                if use_thread:
                    future = self.executor.submit(exception_catcher, function_to_wrap, self, *args, **kwargs)
                    try:
                        content = yield future
                    except Exception:
                        self.set_status(500)
                        self.write("Nested exception at:\n")
                        self.write(traceback.format_exc())
                        self.write("Nested exception was:\n")
                        self.write(future.exception().message+"\n")
                        self.finish()
                        return
                else:
                    content = function_to_wrap(self, *args, **kwargs)
                if content == None:
                    return
                if template_file == "json" or template_file == "string":
                    self.write(content)
                elif template_file == "static":
                    logger.info("\n    +- Attempting static")
                    template_path = self.locator.find_file(filename, self.search_dirs)
                    if (template_path not in self.watched_files):
                        tornado.autoreload.watch(template_path)
                        self.watched_files.append(template_path)
                    templatecontent = self.loader.read(template_path)
                    self.write(templatecontent)
                else:
                    # Watch out for the templates...
                    logger.info("\n    +- About to templating")
                    template_path = template_file + (not template_file.endswith(".mustache") and ".mustache" or "")
                    logger.info(self.search_dirs)
                    logger.info(template_path)
                    template_path = self.locator.find_file(template_path, self.search_dirs)
                    logger.info(template_path)
                    if (template_path not in self.watched_files):
                        tornado.autoreload.watch(template_path)
                        self.watched_files.append(template_path)
                    if (isinstance(content, str)):
                        content = {"body": content}
                    context = {}
                    context['request'] = self

                    context['curr_user'] = {}
                    # if self.session['user.userid']:
                    #     driver = config.papercup.get('drivers',{}).get('users',None)
                    #     user = None
                    #     if (driver):
                    #         user = driver.get_user(self.session['user.userid'])

                    #     # package basic user information for the template to use
                    #     if user:
                    #         # Include an MD5 hash of the user's email, for connection with other services (Gravitar, etc)
                    #         m = hashlib.md5()
                    #         m.update( user.email )

                    #         context['curr_user'] = {
                    #             'id' : user.uid,
                    #             'name' : user.name,
                    #             'email' : user.email,
                    #             'email_hash' : m.hexdigest(),
                    #             'admin' : user.admin,
                    #         }
                    #         if getattr(user,'role', False):
                    #             context['curr_user'].update({
                    #                 'role' : user.role,
                    #                 'role_name' : user.role_name.name,
                    #                 'permissions' : user.role_name.user_permissions
                    #             })

                    templatecontent = self.loader.read(template_path)
                    #logger.info(templatecontent)
                    self.write(self.renderer.render(templatecontent, content, context))
                self.finish()
            except Exception:
                self.set_status(500)
                self.write("Exception at:\n")
                self.write(traceback.format_exc())
                self.finish()
                return
        return gen.coroutine(wrapper)
    return template_wrapper
