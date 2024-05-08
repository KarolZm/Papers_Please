from datetime import date


class Inspector:

    def __init__(self):
        self.nations = []   #TODO duplicates possible
        self.documents = {}
        self.vaccinations = {}
        self.criminal = ""
        self.expiration_date = date(1982, 11, 22)
        # Possible documents for citizens of Arstotzka
        self.arstotzka_docs = ["passport", "certificate_of_vaccination", "ID_card"]
        # Possible documents for foreigners
        self.foreigner_docs = ["passport", "certificate_of_vaccination", "access_permit",
                               "work_pass", "grant_of_asylum", "diplomatic_authorization"]
        # All countries set
        self.countries = {"Arstotzka", "Antegria", "Impor", "Kolechia", "Obristan", "Republia", "United Federation"}
        for country in self.countries:
            self.documents[country] = []
            self.vaccinations[country] = []
        else:
            self.documents["Workers"] = []
        # Common attributes
        self.common_attributes = {"ID number", "NAME", "NATION", "DOB", "SEX"}

    def inspect(self, entrant):
        """
        Method used to inspect a specific entrant
        :param entrant:
        :return:
        """
        print(f"Entrant: {entrant}")
        if not entrant:
            return "Entry denied: missing required passport."

        result = ""
        documents = {}  # Documents of entrant with all properties as a dict
        for document, properties in entrant.items():
            properties_kv = properties.split("\n")
            document_properties = {}
            for kv in properties_kv:
                property_key = kv.split(": ")[0].strip().replace("#", " number")
                property_value = kv.split(": ")[1].strip()
                document_properties[property_key] = property_value
            document_name = document.replace("_", " ")
            documents[document_name] = document_properties
        print(f"Documents: {documents}")
        citizen = {}
        # Fill citizen attributes and look for data conflicts
        for document, properties in documents.items():
            for attribute, value in properties.items():

                # Check if the citizen is a wanted criminal
                if attribute == "NAME":
                    name = value.split(", ")[1] + " " + value.split(", ")[0]
                    if self.criminal == name:
                        result = "Detainment: Entrant is a wanted criminal."
                        return result

                # Check for document's data mismatch
                if attribute in citizen.keys() and attribute in self.common_attributes and citizen[attribute] != value:
                    result = f'Detainment: {attribute} mismatch.'
                    result = result.replace("NATION", "nationality")
                    result = result.replace("NAME", "name")
                    result = result.replace("DOB", "date of birth")

                    return result

                # Check for document expiration date
                if attribute == "EXP":
                    exp_date = value.split(".")
                    exp_year = int(exp_date[0])
                    exp_month = int(exp_date[1])
                    exp_day = int(exp_date[2])

                    if date(exp_year, exp_month, exp_day) <= self.expiration_date:
                        result = f"Entry denied: {document} expired."
                        # return result

                # Add attribute to citizen's data
                if attribute not in citizen.keys():
                    citizen[attribute] = value

        print(f"Citizen: {citizen}")

        # Check for nationality permission
        if citizen["NATION"] not in self.nations:
            result = "Entry denied: citizen of banned nation."
            return result

        # Check required documents
        for document in self.documents[citizen["NATION"]]:
            if document in documents.keys():
                continue
            if document != "access permit":
                result = f"Entry denied: missing required {document}."
                return result
            else:
                if not any(doc in documents.keys() for doc in ["grant of asylum", "diplomatic authorization"]):
                    result = f"Entry denied: missing required {document}."
                    return result
                elif "diplomatic authorization" in documents.keys() and "Arstotzka" not in citizen["ACCESS"].split(", "):
                    result = f"Entry denied: invalid diplomatic authorization."
                    return result

        # Check required vaccinations
        for vaccination in self.vaccinations[citizen["NATION"]]:
            if vaccination not in citizen['VACCINES'].split(", "):
                result = f"Entry denied: missing required {vaccination} vaccination."
                return result

        if result:
            # already exists a reason for deny
            return result

        if citizen["NATION"] == "Arstotzka":
            result = "Glory to Arstotzka."
        else:
            result = "Cause no trouble."
        return result

    def receive_bulletin(self, bulletin):
        """
        Method used to update procedures and regulations.
        :param bulletin:
        :return:
        """
        print(bulletin)
        regulations = bulletin.split("\n")
        for regulation in regulations:
            if "citizens" in regulation:
                self.__update_allowed_nations(regulation)
            elif all(word in regulation for word in ["require", "vaccination"]):
                self.__update_required_vaccinations(regulation)
            elif "require" in regulation:
                self.__update_required_documents(regulation)
            elif "Wanted by the State" in regulation:
                self.criminal = regulation.split(": ")[1]
            else:
                raise Exception("Unknown regulation!")

        print(f"Allowed nations: {self.nations}")
        print(f"Required documents: {self.documents}")
        print(f"Required vaccinations: {self.vaccinations}")
        print(f"Wanted criminal: {self.criminal}")

    def __update_required_documents(self, regulation):
        requirement_logic = False if " no longer " in regulation else True  # True = add; False = remove
        regulation_simplified = regulation.replace(" no longer", "")
        regulation_splitted = regulation_simplified.split(" require ")
        who = regulation_splitted[0]
        documents = regulation_splitted[1].split(", ")

        #TODO
        for i in range(len(documents)):
            documents[i] = documents[i].replace("_", " ")
        print(f"Documents for {who}: {documents}")

        if "Citizens" in who:
            nations = who.split("of ")[1].split(", ")
            for nation in nations:
                self.__update_documents_for_group(nation, documents, requirement_logic)
        elif "Foreigners" in who:
            nations = self.countries.copy()
            nations.remove("Arstotzka")
            for nation in nations:
                self.__update_documents_for_group(nation, documents, requirement_logic)
        elif "Workers" in who:
            self.__update_documents_for_group("Workers", documents, requirement_logic)
        elif "Entrants" in who:
            for group in self.documents.keys():
                self.__update_documents_for_group(group, documents, requirement_logic)
        else:
            raise Exception("Unknown group for documents requirement!")

    def __update_required_vaccinations(self, regulation):
        requirement_logic = False if " no longer " in regulation else True  # True = add; False = remove
        regulation_simplified = regulation.replace(" vaccination", "").replace(" no longer", "")
        regulation_splitted = regulation_simplified.split(" require ")
        who = regulation_splitted[0]
        vaccinations = regulation_splitted[1].split(", ")
        if "Citizens" in who:
            nations = who.split("of ")[1].split(", ")
            for nation in nations:
                self.__update_vaccinations_for_nation(nation, vaccinations, requirement_logic)
        elif "Foreigners" in who:
            nations = self.countries.copy()
            nations.remove("Arstotzka")
            for nation in nations:
                self.__update_vaccinations_for_nation(nation, vaccinations, requirement_logic)
        elif "Entrants" in who:
            for nation in self.countries:
                self.__update_vaccinations_for_nation(nation, vaccinations, requirement_logic)
        else:
            raise Exception("Unknown group for vaccination requirement!")

    def __update_documents_for_group(self, group, documents, logic):
        if logic:
            # Add new required documents for a specific group
            self.documents[group].extend(documents)
        else:
            for doc in documents:
                # Remove each document (no longer required) for a specific group
                self.documents[group].remove(doc)

    def __update_vaccinations_for_nation(self, nation, vaccinations, logic):
        if logic:
            # Add new required vaccinations for a specific nation
            self.vaccinations[nation].extend(vaccinations)
        else:
            for vacc in vaccinations:
                # Remove each vaccination (no longer required) for a specific nation
                self.vaccinations[nation].remove(vacc)

    def __update_allowed_nations(self, regulation):
        nations = regulation.split("of ")[1].split(", ")
        if "Allow" in regulation:
            self.nations.extend(nations)
        elif "Deny" in regulation:
            for nation in nations:
                self.nations.remove(nation)
        else:
            raise Exception("Unknown command for updating allowed nations!")
