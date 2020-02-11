from tests.test_kim_edn import PyTest


COMMENTEDDOC = '{\n  ; property-id\n  "property-id"           "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass" ; property id containing the unique ID of the property.\n  ; property-title\n  "property-title" ; containing a one-line title for the property\n  "Atomic mass"    ; the title is the Atomic mass\n  "property-description"  "The atomic mass of the element"\n  "species" ; species is followed by a map which must contain the following standard keys-value pairs\n  {\n    "type"         "string"\n    "has-unit"     false ; species does not have a unit\n    "extent"       [] ; species is a scalar\n    "required"     true ; it is required to be reported in every instance of the property\n    "description"  "Element symbol of the species"\n  }\n  "mass" {\n    "type"         "float"\n    "has-unit"     true\n    "extent"       []\n    "required"     true\n    "description"  "Mass of a single atom of the species"\n  }\n}'

DOC = '{\n  "property-id"           "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass"\n  "property-title"        "Atomic mass"\n  "property-description"  "The atomic mass of the element"\n  "species" {\n    "type"         "string"\n    "has-unit"     false\n    "extent"       []\n    "required"     true\n    "description"  "Element symbol of the species"\n  }\n  "mass" {\n    "type"         "float"\n    "has-unit"     true\n    "extent"       []\n    "required"     true\n    "description"  "Mass of a single atom of the species"\n  }\n}'


edn_file = 'tests/fixtures/properties/atomic-mass/2016-05-11-brunnels@noreply.openkim.org/atomic-mass.edn'
commented_edn_file = 'tests/fixtures/atomic-mass-commented.edn'


class TestComment:
    """Test the commented edn string.

    Make sure the kim_edn utility can handle the comments in the string
    """

    def test_load(self):
        doc = self.kim_edn.load(edn_file)
        cdoc = self.kim_edn.load(commented_edn_file)

        self.assertEqual(doc, cdoc)

    def test_comment(self):
        cdoc = self.kim_edn.loads(COMMENTEDDOC)
        doc = self.kim_edn.loads(DOC)

        self.assertEqual(cdoc, doc)


class TestPyTestComment(TestComment, PyTest):
    pass
