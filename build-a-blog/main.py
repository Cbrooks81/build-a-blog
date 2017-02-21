import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))



class Blog(db.Model):
    topic = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):
    def render_blog_list(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5;")
        self.render("blog_list.html",blogs = blogs)

    def get(self):
        self.render_blog_list()

class NewBlogHandler(Handler):
    def render_new_post(self,topic="",blog="", error=""):
        self.render("new_post_form.html", topic=topic, blog=blog, error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        topic = self.request.get("topic")
        blog = self.request.get("blog")


        if topic and blog:
            blog = Blog(topic = topic, blog = blog)
            blog.put()

            self.redirect("/blog/"+ str(blog.key().id()))
        else:
            error = "please enter both a topic and a blog"
            self.render_new_post(topic, blog, error)

class ViewBlogHandler(Handler):

    def get(self, id):

        blog_id = Blog.get_by_id(int(id))
        self.render("single_blog.html", blog_id=blog_id)






app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newblog', NewBlogHandler),
    webapp2.Route('/blog/<id:\d+>', ViewBlogHandler)
], debug=True)
