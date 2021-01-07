import smtplib
import ssl
import random
import argparse


def parse():
    parser = argparse.ArgumentParser(
        description="""
            Create a secret santa pool and send out results. Warning: if the debug tag (-d) is not set, 
            emails will be sent automatically. The purpose of this is to keep the pairs anonymous from even the sender 
            by default. If you would like to see results, set the -v tag.
        """)
    parser.add_argument('participants_path', metavar='participants', type=str,
                        help='path to a file containing newline delimited list of participants in form "f_name l_name,_email". See example.txt for more info',
                        nargs='?',
                        default='./example.txt')
    parser.add_argument('sender_email', type=str,
                        help='Email address from which secret santas will be sent their recipients',
                        nargs='?',
                        default='dummy@email.com')
    parser.add_argument('sender_password', type=str,
                        help='Password for sender email',
                        nargs='?',
                        default='securepassword123')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='If true, emails will be sent. If false, generated pairs will be printed to console (use to run a few test simulations perhaps)')
    parser.add_argument('-p', '--port', type=str, default='465')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    return args.participants_path, args.sender_email, args.sender_password, args.debug, args.port, args.verbose


def get_participants(infile):
    participants = []
    with open(infile) as infile:
        for line in infile:
            arr = line.split(',')
            if arr[1].endswith('\n'):
                arr[1] = arr[1][:-1]
            participants.append((arr[0].strip(), arr[1].strip()))
    return participants


def create_random_pairs(participants):
    # Create indexed list of names, emails, and init pairs dict
    names = [x[0] for x in participants]
    emails = [x[1] for x in participants]
    pairs = dict.fromkeys(emails)
    random.shuffle(names)

    # Keep shuffling names array until no name-email index pairs match
    while True:
        shuffled = True
        for i in range(len(names)):
            if participants[i][0] == names[i]:
                shuffled = False
                break
        if shuffled:
            for i in range(len(names)):
                pairs[emails[i]] = (participants[i][0], names[i])
            return pairs
        random.shuffle(names)


def send_emails(pairs, sender_email, sender_password, port):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, sender_password)
        for email in pairs.keys():
            tup = pairs[email]
            message = f"Subject: Secret Santa \n\nDear {tup[0]}, \n\nYour secret santa recipient is {tup[1]}. Don't tell anyone.\n\n Best regards,\n your mysterious benefactor"
            server.sendmail(
                sender_email, email, message)


def run():
    infile, sender_email, sender_password, debug, port, verbose = parse()
    participants = get_participants(infile)
    pairs = create_random_pairs(participants)
    if debug:
        print('=====DEBUG RESULTS=====')
        print([f'{pairs[x][0]}({x}) got {pairs[x][1]}' for x in pairs.keys()])
    else:
        send_emails(pairs, sender_email, sender_password, port)
        if verbose:
            print(
                f'=====EMAILS WERE SENT FROM "{sender_email}" AS FOLLOWS=====')
            print([f'{pairs[x][0]}({x}) got {pairs[x][1]}' for x in pairs.keys()])
        else:
            print(
                "Emails sent! If you're a participant as well, check your email for your recipient.")
    print('\nHappy Holidays!')


if __name__ == "__main__":
    run()
