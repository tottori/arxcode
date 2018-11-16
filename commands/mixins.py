"""
Mixins for commands
"""
from server.utils.exceptions import CommandError
from django.db.models import Q


class ArxCommmandMixin(object):
    """Mixin class for Arx commands"""
    error_class = CommandError

    def check_switches(self, switch_set):
        """Checks if the commands switches are inside switch_set"""
        return set(self.switches) & set(switch_set)

    def search(self, args):
        """Standardizes performing a search for caller"""
        ret = self.caller.search(args)
        if not ret:
            raise self.error_class("Nothing found.")
        return ret

    def character_search(self, args, allow_npc=False):
        """Returns a Character object using given args."""
        from typeclasses.characters import Character
        try:
            if allow_npc:
                return Character.objects.get(db_key__iexact=args)
            else:
                return Character.objects.get(db_key__iexact=args, roster__isnull=False)
        except Character.DoesNotExist:
            raise self.error_class("Could not find a character using '%s'." % args)

    def dompc_search(self, args, only_players=True):
        """Tries to find a PlayerOrNpc with name matching args."""
        from world.dominion.models import PlayerOrNpc
        try:
            if only_players:
                return PlayerOrNpc.objects.get(player__username__iexact=args)
            try:
                return PlayerOrNpc.objects.get(Q(player__username__iexact=args) | Q(npc_name__iexact=args))
            except PlayerOrNpc.MultipleObjectsReturned:
                return PlayerOrNpc.objects.get(player__username__iexact=args)
        except PlayerOrNpc.DoesNotExist:
            raise self.error_class("Could not find '%s'." % args)

    @property
    def called_by_staff(self):
        """Whether caller has staff permissions"""
        return self.caller.check_permstring("builders")

    def get_by_name_or_id(self, cls, args, field_name="name", check_contains_first=True):
        """Gets a given class by ID or a unique text field (default of 'name')"""
        err = "No %s found using '%s'." % (cls.__name__, args)
        try:
            if args.isdigit():
                return cls.objects.get(id=args)
            else:
                if check_contains_first:
                    try:
                        kwargs = {"%s__icontains" % field_name: args}
                        return cls.objects.get(**kwargs)
                    except cls.MultipleObjectsReturned:
                        err = "More than one %s found with '%s'; be specific." % (cls.__name__, args)
                        try:
                            kwargs = {"%s__iexact" % field_name: args}
                            return cls.objects.get(**kwargs)
                        except cls.MultipleObjectsReturned:
                            raise self.error_class(err)
                else:
                    kwargs = {"%s__iexact" % field_name: args}
                    return cls.objects.get(**kwargs)
        except (ValueError, TypeError, cls.DoesNotExist):
            raise self.error_class(err)


class FormCommandMixin(object):
    """Mixin to have command act as a form"""
    form_class = None
    form_attribute = ""
    form_initial_kwargs = []

    @property
    def form(self):
        """Returns the RPEventCreateForm for the caller"""
        proj = self.caller.attributes.get(self.form_attribute)
        if not proj:
            return
        return self.form_class(proj, author=self.caller.roster)

    def create_form(self):
        self.caller.attributes.add(self.form_attribute, dict(self.form_initial_kwargs))
        self.display_form()

    def display_form(self):
        form = self.form
        if not form:
            self.msg("You are not presently creating a %s." % self.form_class.Meta.model.__name__)
            return
        self.msg(form.display())

    def submit_form(self):
        form = self.form
        if not form.is_valid():
            raise CommandError(form.display_errors())
        new_object = form.save()
        self.msg("%s(#%s) created." % (new_object, new_object.id))
        self.caller.attributes.remove(self.form_attribute)
