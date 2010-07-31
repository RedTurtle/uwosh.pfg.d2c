from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import registerATCT
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from uwosh.pfg.d2c.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentAdapter
from zope.interface import implements
from Products.Archetypes.Field import FileField
from Products.Archetypes.Field import ObjectField
from Products.CMFCore.utils import getToolByName
    
FormSaveData2ContentAdapterSchema = ATFolderSchema.copy() + FormAdapterSchema.copy() + \
    Schema((
        BooleanField('avoidSecurityChecks',
            default=True,
            widget=BooleanWidget(label="Avoid Security Checks",
                description="""
                Avoid checking if the user has permission to create the content
                data. You will almost always want this checked; otherwise,
                anonymous users will most likely not be able to submit your
                forms.
                """,)
        )
    ))

class FormSaveData2ContentAdapter(ATFolder, FormActionAdapter):
    """A form action adapter that will save form input data and 
       return it in csv- or tab-delimited format."""

    implements(IFormSaveData2ContentAdapter)
    schema = FormSaveData2ContentAdapterSchema

    meta_type = portal_type = 'FormSaveData2ContentAdapter'
    archetype_name = 'Save Data to Content Adapter'

    security       = ClassSecurityInfo()
    
    def createEntry(self):
        id = self.generateUniqueId()
        if self.getAvoidSecurityChecks():
            pt = getToolByName(self, 'portal_types')
            type_info = pt.getTypeInfo("FormSaveData2ContentEntry")
            ob = type_info._constructInstance(self, id)
            # CMFCore compatibility
            if hasattr(type_info, '_finishConstruction'):
                return type_info._finishConstruction(ob)
            else:
                return ob
        else:
            self.invokeFactory("FormSaveData2ContentEntry", id)
            return self[id]
    
    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        """
        magic done here...
        """

        obj = self.createEntry()
        
        for field in self.fgFields():
            name = field.getName()
            value = REQUEST.form.get(name)
            if field.__class__ == FileField:
                name += '_file'
                if value.filename:
                    field.set(obj, value)
            else:
                field.set(obj, value)
        
registerATCT(FormSaveData2ContentAdapter, PROJECTNAME)
