import gitwrapper
import solventwrapper
import shutil
import os
import unittest
import upseto
import osmosiswrapper
import tempfile
import subprocess


class Test(unittest.TestCase):
    def setUp(self):
        self.osmosisPair = osmosiswrapper.LocalAndOfficial()
        gitwrapper.setUp()
        self.fixture()
        self.cleanLocalClonesDir()
        self.resetFakeMount()

    def resetFakeMount(self):
        if os.path.exists("build/mount"):
            os.unlink("build/mount")
        mount = subprocess.check_output(["mount"])
        with open("build/mount", "w") as f:
            f.write("#!/bin/sh\ncat %s/build/mount.txt\n" % os.getcwd())
        os.chmod("build/mount", 0755)
        with open("build/mount.txt", "w") as f:
            f.write(mount)

    def cleanLocalClonesDir(self):
        shutil.rmtree(gitwrapper.localClonesDir())
        os.makedirs(gitwrapper.localClonesDir())

    def tearDown(self):
        gitwrapper.tearDown()
        if self.osmosisPair is not None:
            self.osmosisPair.exit()

    def fixture(self):
        self.project1 = gitwrapper.GitHub("project1")
        self.project2 = gitwrapper.GitHub("project2")
        self.requiringProject = gitwrapper.GitHub("requiringProject")

        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone2 = gitwrapper.LocalClone(self.project2)
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        self.assertEquals(self.project1.hash('master'), localClone1.hash())
        self.assertEquals(self.project2.hash('master'), localClone2.hash())
        self.assertEquals(self.requiringProject.hash(), localRequiringProject.hash())

        solventwrapper.upseto(localRequiringProject, "addRequirement project1")
        solventwrapper.upseto(localRequiringProject, "addRequirement project2")
        localRequiringProject.addCommitPushManifest()

        self.recursiveProject = gitwrapper.GitHub("recursiveProject")
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.upseto(localRecursiveProject, "addRequirement requiringProject")
        localRecursiveProject.addCommitPushManifest()

    def test_Fixture(self):
        self.assertNotIn('/usr', upseto.__file__)
        import solvent
        self.assertNotIn('/usr', solvent.__file__)
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.upseto(localRecursiveProject, "fulfillRequirements")
        lines = solventwrapper.upseto(localRecursiveProject, "checkRequirements --show")
        self.assertEquals(len([l for l in lines.split("\n") if 'file:///' in l]), 4)

    def test_SubmitANonUpsetoedProject(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        self.assertFalse(localClone1.fileExists("build/product1"))
        localClone1.writeFile("build/product1", "product1 contents")
        self.assertTrue(localClone1.fileExists("build/product1"))

        solventwrapper.run(localClone1, "submitbuild")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__dirty' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.assertFalse(localClone1.fileExists("build/product1"))
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))

    def test_SubmitANonUpsetoedProject_FailsIfWorkspaceIsSullied(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone2 = gitwrapper.LocalClone(self.project2)

        solventwrapper.runShouldFail(localClone1, "submitbuild", "sullied", env=dict(SOLVENT_CLEAN="yes"))

    def test_ConfigurationMissingOfficialOsmosis(self):
        configuration = tempfile.NamedTemporaryFile()
        solventwrapper.configurationFile = configuration.name
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.runShouldFail(localClone1, "submitbuild", "empty")

        configuration.write("key: value\n")
        configuration.flush()
        solventwrapper.runShouldFail(localClone1, "submitbuild", "official")

    def test_SubmitBuildNotAllowedFromANonGitProject(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        self.osmosisPair.exit()
        solventwrapper.runShouldFail(localClone1, "submitbuild", "osmosis")
        self.osmosisPair = None

    def test_SubmitANonUpsetoedProjectOfficialBuild(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        localClone1.writeFile("build/product1", "product1 contents")

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__officialcandidate' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))

    def test_SubmitAndApprove(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        localClone1.writeFile("build/product1", "product1 contents")

        solventwrapper.run(localClone1, "submitbuild", env=dict(SOLVENT_CLEAN="yes"))
        solventwrapper.run(localClone1, "approve", env=dict(SOLVENT_CLEAN="yes"))

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__clean' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.assertFalse(localClone1.fileExists("build/product1"))
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))

    def test_SubmitAndApprove_Official(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        localClone1.writeFile("build/product1", "product1 contents")

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")
        solventwrapper.run(localClone1, "approve")

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__official' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.assertFalse(localClone1.fileExists("build/product1"))
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))

    def test_FulfillUpsetoRequirements(self):
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone1.writeFile("build/product1", "product1 contents")
        solventwrapper.upseto(localRequiringProject, "fulfillRequirements")
        localRequiringProject.writeFile("build/product2", "product2 contents")

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localRequiringProject, "submitbuild")
        solventwrapper.run(localRequiringProject, "approve")
        solventwrapper.configureAsNonOfficial()

        self.cleanLocalClonesDir()
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.run(localRecursiveProject, "checkrequirements")
        solventwrapper.run(localRecursiveProject, "fulfillrequirements")

        self.assertTrue(localClone1.fileExists("build/product1"))
        self.assertTrue(localRequiringProject.fileExists("build/product2"))

        solventwrapper.run(localRecursiveProject, "checkrequirements")
        labels = self.osmosisPair.local.client().listLabels()
        self.assertEquals(len(labels), 1)
        label = labels[0]
        self.osmosisPair.local.client().eraseLabel(label)
        solventwrapper.run(localRecursiveProject, "checkrequirements")
        self.osmosisPair.official.client().eraseLabel(label)
        solventwrapper.runShouldFail(localRecursiveProject, "checkrequirements", "label")

    def test_NoRequirements_FulfillDoesNothing(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.run(localClone1, "fulfillrequirements")

    def test_FulfillUpsetoRequirements_MoreThanOneProject(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone1.writeFile("build/product1", "product1 contents")
        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")
        solventwrapper.run(localClone1, "approve")

        self.cleanLocalClonesDir()
        localClone2 = gitwrapper.LocalClone(self.project2)
        localClone2.writeFile("build/product2", "product2 contents")
        solventwrapper.run(localClone2, "submitbuild")
        solventwrapper.run(localClone2, "approve")
        solventwrapper.configureAsNonOfficial()

        self.cleanLocalClonesDir()
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        solventwrapper.run(localRequiringProject, "fulfillrequirements")

        self.assertTrue(localClone1.fileExists("build/product1"))
        self.assertTrue(localClone2.fileExists("build/product2"))

    def test_FulfillUpsetoRequirements_NoOfficialBuild(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone1.writeFile("build/product1", "product1 contents")
        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")

        self.cleanLocalClonesDir()
        localClone2 = gitwrapper.LocalClone(self.project2)
        localClone2.writeFile("build/product2", "product2 contents")
        solventwrapper.run(localClone2, "submitbuild")
        solventwrapper.run(localClone2, "approve")
        solventwrapper.configureAsNonOfficial()

        self.cleanLocalClonesDir()
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        solventwrapper.runShouldFail(localRequiringProject, "fulfillrequirements", "build")

    def createBuildProduct(self):
        self.producer = gitwrapper.GitHub("producer")
        localProducer = gitwrapper.LocalClone(self.producer)
        localProducer.writeFile("build/theDirectory/theProduct", "the contents")
        solventwrapper.configureAsOfficial()
        solventwrapper.run(localProducer, "submitproduct theProductName build")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__officialcandidate' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        solventwrapper.run(localProducer, "approve --product=theProductName")
        return localProducer

    def test_createBuildProduct(self):
        self.createBuildProduct()

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

        self.cleanLocalClonesDir()
        solventwrapper.run(
            gitwrapper.localClonesDir(),
            "bring --repository=producer --product=theProductName --hash=%s --destination=%s" % (
                self.producer.hash(), gitwrapper.localClonesDir()))
        self.assertTrue(os.path.isdir(os.path.join(gitwrapper.localClonesDir(), "theDirectory")))
        self.assertTrue(os.path.exists(
            os.path.join(gitwrapper.localClonesDir(), "theDirectory", "theProduct")))

    def test_fulfillRequirementsLabelDoesNotExistInLocalOsmosis(self):
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone1.writeFile("build/product1", "product1 contents")
        solventwrapper.upseto(localRequiringProject, "fulfillRequirements")
        localRequiringProject.writeFile("build/product2", "product2 contents")

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localRequiringProject, "submitbuild")
        solventwrapper.run(localRequiringProject, "approve")
        solventwrapper.configureAsNonOfficial()

        labels = self.osmosisPair.local.client().listLabels()
        self.assertEquals(len(labels), 1)
        self.osmosisPair.local.client().eraseLabel(labels[0])

        self.cleanLocalClonesDir()
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.run(localRecursiveProject, "fulfillrequirements")

        self.assertTrue(localClone1.fileExists("build/product1"))
        self.assertTrue(localRequiringProject.fileExists("build/product2"))

    def test_noOfficialObjectStoreConfigured(self):
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone1.writeFile("build/product1", "product1 contents")
        solventwrapper.upseto(localRequiringProject, "fulfillRequirements")
        localRequiringProject.writeFile("build/product2", "product2 contents")

        solventwrapper.configureNoOfficial()
        solventwrapper.configureAsOfficial()
        solventwrapper.run(localRequiringProject, "submitbuild")
        solventwrapper.run(localRequiringProject, "approve")

        self.cleanLocalClonesDir()
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.run(localRecursiveProject, "fulfillrequirements")

        self.assertTrue(localClone1.fileExists("build/product1"))
        self.assertTrue(localRequiringProject.fileExists("build/product2"))

    def test_createBuildProduct_bringExactVersionFromManifestFile(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()))

        solventwrapper.run(
            localClone1, "bring --repository=producer --product=theProductName --destination=%s" % (
                os.path.join(localClone1.directory(), "build", "theProductDir")))
        self.assertTrue(os.path.isdir(os.path.join(
            localClone1.directory(), "build", "theProductDir", "theDirectory")))
        self.assertTrue(os.path.exists(os.path.join(
            localClone1.directory(), "build", "theProductDir", "theDirectory", "theProduct")))

    def test_invalidInputForAddRequirementCommandLine(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.runShouldFail(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            "thisisnotagiturl", self.producer.hash()), "invalid")
        solventwrapper.runShouldFail(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()[: -2]), "invalid")
        solventwrapper.runShouldFail(
            localClone1, "bring --repository=producer --product=theProductName --destination=%s" % (
                os.path.join(localClone1.directory(), "build", "theProductDir")), "requirement")

    def test_updateRequirement(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        self.assertNotEquals(self.producer.hash()[-2:], "00")
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()[: -2] + "00"))
        previous = localClone1.readFile("solvent.manifest")
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()))
        self.assertEquals(len(localClone1.readFile("solvent.manifest")), len(previous))

        solventwrapper.run(
            localClone1, "bring --repository=producer --product=theProductName --destination=%s" % (
                os.path.join(localClone1.directory(), "build", "theProductDir")))

        solventwrapper.run(
            localClone1, "removerequirement --originURLBasename=producer")
        solventwrapper.runShouldFail(
            localClone1, "bring --repository=producer --product=theProductName --destination=%s" % (
                os.path.join(localClone1.directory(), "build", "theProductDir")), "requirement")

    def test_workDirty(self):
        self.producer = gitwrapper.GitHub("producer")
        localProducer = gitwrapper.LocalClone(self.producer)
        localProducer.writeFile("build/theDirectory/theProduct", "the contents")
        localProducer.writeFile("imaketheprojectdirty", "dirty dirty boy")
        localProducer.writeFile("../isullytheworkspace", "and my pants too")
        solventwrapper.runShouldFail(
            localProducer, "submitproduct theProductName build", "sullied",
            env=dict(SOLVENT_CLEAN="yes"))
        solventwrapper.run(localProducer, "submitproduct theProductName build")

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__dirty' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

        solventwrapper.runWhatever(
            localProducer.directory(),
            "coverage run --parallel-mode -m solvent.cheating --configurationFile=%s "
            "changestate --fromState=dirty --toState=official --product=theProductName" %
            solventwrapper.configurationFile)

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

    def test_FetchObjectStoresConfiguration(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        output = solventwrapper.run(localClone1, "printobjectstores").strip()
        self.assertEquals(output, "localhost:%d+localhost:%d" % (
            self.osmosisPair.local.port(), self.osmosisPair.official.port()))

    def test_PrintDependantLabel(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()))
        expectedLabel = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        label = solventwrapper.run(
            localClone1, "printlabel --repositoryBasename=producer --product=theProductName").strip()
        self.assertEquals(label, expectedLabel)

    def createAllStates(self):
        localProducer = self.createBuildProduct()
        solventwrapper.configureAsNonOfficial()
        solventwrapper.run(
            localProducer, "submitproduct theProductName build", env=dict(SOLVENT_CLEAN="yes"))
        solventwrapper.run(
            localProducer, "approve --product=theProductName", env=dict(SOLVENT_CLEAN="yes"))
        solventwrapper.run(localProducer, "submitproduct theProductName build")

        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()))
        officialLabel = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        cleanLabel = 'solvent__producer__theProductName__%s__clean' % self.producer.hash()
        dirtyLabel = 'solvent__producer__theProductName__%s__dirty' % self.producer.hash()

        getCleanLabel = lambda: solventwrapper.run(
            localClone1, "printlabel --repositoryBasename=producer --product=theProductName",
            env=dict(SOLVENT_CLEAN="Yes")).strip()
        getDirtyLabel = lambda: solventwrapper.run(
            localClone1, "printlabel --repositoryBasename=producer --product=theProductName").strip()
        noCleanLabel = lambda: solventwrapper.runShouldFail(
            localClone1, "printlabel --repositoryBasename=producer --product=theProductName", "requirement",
            env=dict(SOLVENT_CLEAN="yes"))
        noDirtyLabel = lambda: solventwrapper.runShouldFail(
            localClone1, "printlabel --repositoryBasename=producer --product=theProductName", "requirement")
        return dict(
            getCleanLabel=getCleanLabel, getDirtyLabel=getDirtyLabel,
            noCleanLabel=noCleanLabel, noDirtyLabel=noDirtyLabel,
            localClone1=localClone1, officialLabel=officialLabel,
            cleanLabel=cleanLabel, dirtyLabel=dirtyLabel)

    def test_priorityBetweenStates_OfficialBuild(self):
        created = self.createAllStates()
        solventwrapper.configureAsOfficial()
        self.assertEquals(created['getCleanLabel'](), created['officialLabel'])
        self.osmosisPair.local.client().eraseLabel(created['officialLabel'])
        self.assertEquals(created['getCleanLabel'](), created['officialLabel'])
        self.osmosisPair.official.client().eraseLabel(created['officialLabel'])
        created['noCleanLabel']()

    def test_priorityBetweenStates_CleanBuild(self):
        created = self.createAllStates()
        solventwrapper.configureAsNonOfficial()
        self.assertEquals(created['getCleanLabel'](), created['officialLabel'])
        self.osmosisPair.local.client().eraseLabel(created['officialLabel'])
        self.assertEquals(created['getCleanLabel'](), created['cleanLabel'])
        self.osmosisPair.local.client().eraseLabel(created['cleanLabel'])
        self.assertEquals(created['getCleanLabel'](), created['officialLabel'])
        self.osmosisPair.official.client().eraseLabel(created['officialLabel'])
        self.assertEquals(created['getCleanLabel'](), created['cleanLabel'])
        self.osmosisPair.official.client().eraseLabel(created['cleanLabel'])
        created['noCleanLabel']()

    def test_priorityBetweenStates_DirtyBuild(self):
        created = self.createAllStates()
        solventwrapper.configureAsNonOfficial()
        self.assertEquals(created['getDirtyLabel'](), created['officialLabel'])
        self.osmosisPair.local.client().eraseLabel(created['officialLabel'])
        self.assertEquals(created['getDirtyLabel'](), created['cleanLabel'])
        self.osmosisPair.local.client().eraseLabel(created['cleanLabel'])
        self.assertEquals(created['getDirtyLabel'](), created['dirtyLabel'])
        self.osmosisPair.local.client().eraseLabel(created['dirtyLabel'])
        self.assertEquals(created['getDirtyLabel'](), created['officialLabel'])
        self.osmosisPair.official.client().eraseLabel(created['officialLabel'])
        self.assertEquals(created['getDirtyLabel'](), created['cleanLabel'])
        self.osmosisPair.official.client().eraseLabel(created['cleanLabel'])
        self.assertEquals(created['getDirtyLabel'](), created['dirtyLabel'])
        self.osmosisPair.official.client().eraseLabel(created['dirtyLabel'])
        created['noDirtyLabel']()

    def test_solventCanBeConfiguredFromTheEnvironment(self):
        self.producer = gitwrapper.GitHub("producer")
        localProducer = gitwrapper.LocalClone(self.producer)
        localProducer.writeFile("build/theDirectory/theProduct", "the contents")
        localProducer.writeFile("imaketheprojectdirty", "dirty dirty boy")
        localProducer.writeFile("../isullytheworkspace", "and my pants too")
        solventwrapper.runShouldFail(
            localProducer, "submitproduct theProductName build", "sullied",
            env=dict(SOLVENT_CONFIG="CLEAN: yes"))
        solventwrapper.run(localProducer, "submitproduct theProductName build")

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__dirty' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

    def test_localize(self):
        self.createBuildProduct()

        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

        self.osmosisPair.local.client().eraseLabel(label)
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [])
        solventwrapper.run(os.getcwd(), "localize --label=%s" % label)
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])

        solventwrapper.run(os.getcwd(), "localize --label=%s" % label)

        self.osmosisPair.local.client().eraseLabel(label)
        solventwrapper.runShouldFail(
            os.getcwd(), "localize --label=%s" % label, "official",
            env=dict(SOLVENT_CONFIG="WITH_OFFICIAL_OBJECT_STORE: No"))

    def test_createBuildProduct_bringLabel(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        label = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        solventwrapper.run(
            gitwrapper.localClonesDir(), "bringlabel --label=%s --destination=%s" % (
                label, gitwrapper.localClonesDir()))
        self.assertTrue(os.path.isdir(os.path.join(
            gitwrapper.localClonesDir(), "theDirectory")))
        self.assertTrue(os.path.exists(os.path.join(
            gitwrapper.localClonesDir(), "theDirectory", "theProduct")))

    def test_checkSolventRequirements_DependsOnSolvent__build__productName(self):
        self.createBuildProduct()
        self.cleanLocalClonesDir()
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.run(localClone1, "addrequirement --originURL=%s --hash=%s" % (
            self.producer.url(), self.producer.hash()))
        label = 'solvent__producer__theProductName__%s__official' % self.producer.hash()
        buildLabel = 'solvent__producer__build__%s__official' % self.producer.hash()
        solventwrapper.runShouldFail(localClone1, "checkrequirements", "label")
        self.osmosisPair.local.client().renameLabel(label, buildLabel)
        solventwrapper.run(localClone1, "checkrequirements")

    def test_SubmitTwiceDoesNotWork_ForceWorks(self):
        localClone1 = gitwrapper.LocalClone(self.project1)

        solventwrapper.run(localClone1, "submitbuild")
        solventwrapper.runShouldFail(localClone1, "submitbuild", "already")
        solventwrapper.run(localClone1, "submitbuild --force")
        solventwrapper.runShouldFail(localClone1, "submitbuild", "already")
        solventwrapper.run(localClone1, "submitbuild", env=dict(SOLVENT_CONFIG="FORCE: yes"))

    def test_ProtectAgainstCommonMistakes_ProcMounted(self):
        self.producer = gitwrapper.GitHub("producer")
        localProducer = gitwrapper.LocalClone(self.producer)
        localProducer.writeFile("build/rootfs/etc/config", "the contents")
        os.mkdir(os.path.join(localProducer.directory(), "proc"))
        with open("build/mount.txt", "a") as f:
            f.write("proc on %s/proc type proc (rw,nosuid,nodev,noexec,relatime)\n" % (
                os.path.join(localProducer.directory(), 'build', 'rootfs', 'proc'), ))
        solventwrapper.runShouldFail(
            localProducer, "submitproduct rootfs build/rootfs", "mounted")

        solventwrapper.run(localProducer, "submitproduct rootfs build/rootfs --noCommonMistakesProtection")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__producer__rootfs__%s__dirty' % self.producer.hash()
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)

    def test_ApproveTwiceDoesNotWork_ForceDoesNothing(self):
        localClone1 = gitwrapper.LocalClone(self.project1)

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")
        solventwrapper.run(localClone1, "approve")
        solventwrapper.runShouldFail(localClone1, "approve", "already")
        solventwrapper.runShouldFail(localClone1, "approve", "already", env=dict(
            SOLVENT_CONFIG="FORCE: yes"))

    def test_LabelExists(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        localClone1.writeFile("build/product1", "product1 contents")

        solventwrapper.run(localClone1, "submitbuild")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__dirty' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        solventwrapper.run(localClone1, 'labelexists --label=%s' % label)
        solventwrapper.runShouldFail(localClone1, 'labelexists --label=%sA' % label, "exist")
        solventwrapper.runShouldFail(localClone1, 'labelexists --label=A%s' % label, "exist")
        solventwrapper.runShouldFail(localClone1, 'labelexists --label=A', "exist")
        solventwrapper.runShouldFail(localClone1, 'labelexists --label=%s' % label[:-1], "exist")

# indirect deep dep joined
# remove unosmosed files


if __name__ == '__main__':
    unittest.main()
