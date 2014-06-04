class Element():
    def __init__(self, extension=None, modifierExtension=None):
        self.extension = extension
        self.modifierExtension = modifierExtension


class Section():

    def __init__(self, title=None, code=None, subject=None, content=None):
        self.title = title
        self.code = code
        self.subject = subject

        if content is None:
            self.content = []
        else:
            self.content = content


class Address(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param use: The purpose of this address.
    :param text: A full text representation of the address.
    :param city: The name of the city, town, village or other community or delivery center.
    :param state: Sub-unit of a country with limited sovereignty in a federally organized country. A code may be used if codes are in common use (i.e. US 2 letter state codes).
    :param zip: A postal code designating a region defined by the postal service.
    :param country: Country - a nation as commonly understood or generally accepted.
    :param period: Time period when address was/is in use.
    
    :param line: This component contains the house number, apartment number, street name, street direction, 
P.O. Box number, delivery hints, and similar address information.
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 use=None,
                 text=None,
                 city=None,
                 state=None,
                 zip=None,
                 country=None,
                 period=None,
                 line=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.use = use                                     #home | work | temp | old - purpose of this address
        self.text = text                                     #Text representation of the address
        self.city = city                                     #Name of city, town etc.
        self.state = state                                     #Sub-unit of country (abreviations ok)
        self.zip = zip                                     #Postal code for area
        self.country = country                                     #Country (can be ISO 3166 3 letter code)
        self.period = period                                     #Time period when address was/is in use
        
        if line is None:
            self.line = []                                     #Street name, number, direction & P.O. Box etc
        

class Age(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Attachment(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param contentType: Identifies the type of the data in the attachment and allows a method to be chosen to interpret or render the data. Includes mime type parameters such as charset where appropriate.
    :param language: The human language of the content. The value can be any valid value according to BCP 47.
    :param data: The actual data of the attachment - a sequence of bytes. In XML, represented using base64.
    :param url: An alternative location where the data can be accessed.
    :param size: The number of bytes of data that make up this attachment.
    :param hash: The calculated hash of the data using SHA-1. Represented using base64.
    :param title: A label or set of text to display in place of the data.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 contentType=None,
                 language=None,
                 data=None,
                 url=None,
                 size=None,
                 hash=None,
                 title=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.contentType = contentType                                     #Mime type of the content, with charset etc.
        self.language = language                                     #Human language of the content (BCP-47)
        self.data = data                                     #Data inline, base64ed
        self.url = url                                     #Uri where the data can be found
        self.size = size                                     #Number of bytes of content (if url provided)
        self.hash = hash                                     #Hash of the data (sha-1, base64ed )
        self.title = title                                     #Label to display in place of the data
        
        

class CodeableConcept(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param text: A human language representation of the concept as seen/selected/uttered by the user who entered the data and/or which represents the intended meaning of the user.
    
    :param coding: A reference to a code defined by a terminology system.
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 text=None,
                 coding=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.text = text                                     #Plain text representation of the concept
        
        if coding is None:
            self.coding = []                                     #Code defined by a terminology system
        else:
            self.coding = coding
        

class Coding(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param system: The identification of the code system that defines the meaning of the symbol in the code.
    :param version: The version of the code system which was used when choosing this code. Note that a well-maintained code system does not need the version reported, because the meaning of codes is consistent across versions. However this cannot consistently be assured. and When the meaning is not guaranteed to be consistent, the version SHOULD be exchanged.
    :param code: A symbol in syntax defined by the system. The symbol may be a predefined code or an expression in a syntax defined by the coding system (e.g. post-coordination).
    :param display: A representation of the meaning of the code in the system, following the rules of the system.
    :param primary: Indicates that this code was chosen by a user directly - i.e. off a pick list of available items (codes or displays).
    :param valueSet: The set of possible coded values this coding was chosen from or constrained by.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 system=None,
                 version=None,
                 code=None,
                 display=None,
                 primary=None,
                 valueSet=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.system = system                                     #Identity of the terminology system
        self.version = version                                     #Version of the system - if relevant
        self.code = code                                     #Symbol in syntax defined by the system
        self.display = display                                     #Representation defined by the system
        self.primary = primary                                     #If this code was chosen directly by the user
        self.valueSet = valueSet                                     #Set this coding was chosen from
        
        

class Contact(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param system: Telecommunications form for contact - what communications system is required to make use of the contact.
    :param value: The actual contact details, in a form that is meaningful to the designated communication system (i.e. phone number or email address).
    :param use: Identifies the purpose for the address.
    :param period: Time period when the contact was/is in use.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 system=None,
                 value=None,
                 use=None,
                 period=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.system = system                                     #phone | fax | email | url
        self.value = value                                     #The actual contact details
        self.use = use                                     #home | work | temp | old | mobile - purpose of this address
        self.period = period                                     #Time period when the contact was/is in use
        
        

class Count(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Distance(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Duration(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Extension(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param url: Source of the definition for the extension code - a logical name or a URL.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 url=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.url = url                                     #identifies the meaning of the extension
        
        

class HumanName(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param use: Identifies the purpose for this name.
    :param text: A full text representation of the name.
    :param period: Indicates the period of time when this name was valid for the named person.
    
    :param family: The part of a name that links to the genealogy. In some cultures (e.g. Eritrea) the family name of a son is the first name of his father.
    :param given: Given name.
    :param prefix: Part of the name that is acquired as a title due to academic, legal, employment or nobility status, etc. and that appears at the start of the name.
    :param suffix: Part of the name that is acquired as a title due to academic, legal, employment or nobility status, etc. and that appears at the end of the name.
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 use=None,
                 text=None,
                 period=None,
                 family=None,
                 given=None,
                 prefix=None,
                 suffix=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.use = use                                     #usual | official | temp | nickname | anonymous | old | maiden
        self.text = text                                     #Text representation of the full name
        self.period = period                                     #Time period when name was/is in use
        
        if family is None:
            self.family = []                                     #Family name (often called 'Surname')
        if given is None:
            self.given = []                                     #Given names (not always 'first'). Includes middle names
        if prefix is None:
            self.prefix = []                                     #Parts that come before the name
        if suffix is None:
            self.suffix = []                                     #Parts that come after the name
        

class Identifier(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param use: The purpose of this identifier.
    :param label: A text string for the identifier that can be displayed to a human so they can recognize the identifier.
    :param system: Establishes the namespace in which set of possible id values is unique.
    :param value: The portion of the identifier typically displayed to the user and which is unique within the context of the system.
    :param period: Time period during which identifier is/was valid for use.
    :param assigner: Organization that issued/manages the identifier.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 use=None,
                 label=None,
                 system=None,
                 value=None,
                 period=None,
                 assigner=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.use = use                                     #usual | official | temp | secondary (If known)
        self.label = label                                     #Description of identifier
        self.system = system                                     #The namespace for the identifier
        self.value = value                                     #The value that is unique
        self.period = period                                     #Time period when id is/was valid for use
        self.assigner = assigner                                     #Organization that issued id (may be just text)
        
        

class Money(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Narrative(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param status: The status of the narrative - whether it's entirely generated (from just the defined data or the extensions too), or whether a human authored it and it may contain additional data.
    :param div: The actual narrative content, a stripped down version of XHTML.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 status=None,
                 div=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.status = status                                     #generated | extensions | additional
        self.div = div                                     #Limited xhtml content
        
        

class Period(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param start: The start of the period. The boundary is inclusive.
    :param end: The end of the period. If the end of the period is missing, it means that the period is ongoing.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 start=None,
                 end=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.start = start                                     #Starting time with inclusive boundary
        self.end = end                                     #End time with inclusive boundary, if not ongoing
        
        

class Quantity(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param value: The value of the measured amount. The value includes an implicit precision in the presentation of the value.
    :param comparator: How the value should be understood and represented - whether the actual value is greater or less than the stated value due to measurement issues. E.g. if the comparator is "<" , then the real value is < stated value.
    :param units: A human-readable form of the units.
    :param system: The identification of the system that provides the coded form of the unit.
    :param code: A computer processable form of the units in some unit representation system.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 value=None,
                 comparator=None,
                 units=None,
                 system=None,
                 code=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.value = value                                     #Numerical value (with implicit precision)
        self.comparator = comparator                                     #< | <= | >= | > - how to understand the value
        self.units = units                                     #Unit representation
        self.system = system                                     #System that defines coded unit form
        self.code = code                                     #Coded form of the unit
        
        

class Range(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param low: The low limit. The boundary is inclusive.
    :param high: The high limit. The boundary is inclusive.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 low=None,
                 high=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.low = low                                     #Low limit
        self.high = high                                     #High limit
        
        

class Ratio(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param numerator: The value of the numerator.
    :param denominator: The value of the denominator.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 numerator=None,
                 denominator=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.numerator = numerator                                     #Numerator value
        self.denominator = denominator                                     #Denominator value
        
        

class ResourceReference(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param reference: A reference to a location at which the other resource is found. The reference may a relative reference, in which case it is relative to the service base URL, or an absolute URL that resolves to the location where the resource is found. The reference may be version specific or not. If the reference is not to a FHIR RESTful server, then it should be assumed to be version specific. Internal fragment references (start with '#') refer to contained resources.
    :param display: Plain text narrative that identifies the resource in addition to the resource reference.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 reference=None,
                 display=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.reference = reference                                     #Relative, internal or absolute URL reference
        self.display = display                                     #Text alternative for the resource
        
        

class SampledData(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param origin: The base quantity that a measured value of zero represents. In addition, this provides the units of the entire measurement series.
    :param period: The length of time between sampling times, measured in milliseconds.
    :param factor: A correction factor that is applied to the sampled data points before they are added to the origin.
    :param lowerLimit: The lower limit of detection of the measured points. This is needed if any of the data points have the value "L" (lower than detection limit).
    :param upperLimit: The upper limit of detection of the measured points. This is needed if any of the data points have the value "U" (higher than detection limit).
    :param dimensions: The number of sample points at each time point. If this value is greater than one, then the dimensions will be interlaced - all the sample points for a point in time will be recorded at once.
    :param data: A series of data points which are decimal values separated by a single space (character u20). The special values "E" (error), "L" (below detection limit) and "U" (above detection limit) can also be used in place of a decimal value.
    
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 origin=None,
                 period=None,
                 factor=None,
                 lowerLimit=None,
                 upperLimit=None,
                 dimensions=None,
                 data=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.origin = origin                                     #Zero value and units
        self.period = period                                     #Number of milliseconds between samples
        self.factor = factor                                     #Multiply data by this before adding to origin
        self.lowerLimit = lowerLimit                                     #Lower limit of detection
        self.upperLimit = upperLimit                                     #Upper limit of detection
        self.dimensions = dimensions                                     #Number of sample points at each time point
        self.data = data                                     #Decimal values with spaces, or "E" | "U" | "L"
        
        

class Schedule(Element):
    """
    Short Description: Extensions that cannot be ignored

    Formal Description: May be used to represent additional information that is not part of the basic definition of the resource, and that modifies the understanding of the element that contains it. Usually modifier elements provide negation or qualification. In order to make the use of extensions safe and manageable, there is a strict governance applied to the definition and use of extensions. Though any implementer is allowed to define an extension, there is a set of requirements that SHALL be met as part of the definition of the extension. Applications processing a resource are required to check for modifier extensions.

    :param repeat: Identifies a repeating pattern to the intended time periods.
    :param frequency: Indicates how often the event should occur.
    :param when: Identifies the occurrence of daily life that determines timing.
    :param duration: How long each repetition should last.
    :param units: The units of time for the duration.
    :param count: A total count of the desired number of repetitions.
    :param end: When to stop repeating the schedule.
    
    :param event: Identifies specific time periods when the event should occur.
    
    """
    def __init__(self,
                 extension=None,
                 modifierExtension=None,
                 repeat=None,
                 frequency=None,
                 when=None,
                 duration=None,
                 units=None,
                 count=None,
                 end=None,
                 event=None,
                 ):
        Element.__init__(self, extension=extension, modifierExtension=modifierExtension)
        self.repeat = repeat                                     #Only if there is none or one event
        self.frequency = frequency                                     #Event occurs frequency times per duration
        self.when = when                                     #HS | WAKE | AC | ACM | ACD | ACV | PC | PCM | PCD | PCV - common life events
        self.duration = duration                                     #Repeating or event-related duration
        self.units = units                                     #s | min | h | d | wk | mo | a - unit of time (UCUM)
        self.count = count                                     #Number of times to repeat
        self.end = end                                     #When to stop repeats
        
        if event is None:
            self.event = []                                     #When the event occurs
        