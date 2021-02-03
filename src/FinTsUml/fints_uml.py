import re
import requests
import sys

def filter_hbci(binary_message):
    # according to "FinTS-Basiszeichensätze" in Formals
    invalidHbciChars = re.compile(b'[^\x20-\x7E\xA1-\xFF\x0A\x0D]')
    # replace illegal characters
    filtered = re.sub(invalidHbciChars, b'.', binary_message)
    # add line breaks between segments (except the last one); does not handle nested segments
    separateSegments = re.compile(b'\'(?=.)')
    filtered = re.sub(separateSegments, b'\'\n', filtered)
    return filtered
    
class SendReceiveToggle:
    def __init__(self, names):
        self.arrows = ["->", "<-"]
        self.names = names
        self.stateValues =  [0, 1]
        self.state = 0

    def get_arrow_str(self):
        index = self.state
        arrow_str = f'{self.names[0]} {self.arrows[index]} {self.names[1]}'
        self.state = 1 if self.state == 0 else 0  # toggle
        return self.names[index], arrow_str

# server_url must include host and endpoint, e.g. "/svg/" for svg image
# note that the get request might fail if source is too long
def get_image_from_plantuml(plantuml_src):
    server_url = "http://localhost:8080/svg/"
    # use GET with hex encoding
    server_url += "~h"
    r = requests.get(f'{server_url}'+ bytearray(plantuml_src, "latin1").hex())
    print(r.status_code)
    # res = r.status_code == requests.codes.OK
    r.raise_for_status() # raise exception if code not oka
    return r.content

def get_plantuml_from_source(binary_source):
    hbciRegex = re.compile(rb"(?:Start HBCI message.*\n(.*?)\nEnd HBCI message\n)+?", re.MULTILINE)
    messages = hbciRegex.findall(binary_source)
    messages_filtered = [filter_hbci(m) for m in messages]
    # convert to non-binary string
    messages_filtered = [m.decode('latin-1') for m in messages_filtered]

    participant_names = ["SM", "FinTS"]
    srt = SendReceiveToggle(participant_names)
    diagStrList = []
    diagStrList.append(f'@startuml\n\nparticipant {participant_names[0]}\nparticipant {participant_names[1]}\n')
    for m in messages_filtered:
        name, arrowStr = srt.get_arrow_str()
        diagStrList.append(arrowStr)
        diagStrList.append(f'\nnote over {name}\n')
        diagStrList.append(m)
        diagStrList.append('\nend note\n')
    diagStrList.append('\n@enduml\n')
    diag_str = ''.join(diagStrList)
    # print(diag_str)
    return diag_str


def main():
    if len(sys.argv) < 2:
        print("missing file name")
        sys.exit(1)
        
    filename = sys.argv[1]
    print(f'processing {filename}')
    binary_source = open(filename, 'rb')

    plantuml_src = get_plantuml_from_source(binary_source.read())
    # file_puml = open(filename + '.plantuml', 'w')
    # file_puml.write(plantuml_src)
    # file_puml.close()

    # try/catch
    image = get_image_from_plantuml(plantuml_src)
    save_image = open(filename + '.svg', 'wb')
    save_image.write(image)
    save_image.close()

if __name__ == "__main__":
    main()
