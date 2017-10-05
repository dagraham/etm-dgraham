class Item(dict):
    """

    """

    def __init__(self, string: str = ''):
        dict.__init__(self, entry=string)
        if string:
            ok, res = self.str2item(string)
            if ok:
                self.item['entry'] = self.hsh2str(res)
                self.item.update({res})
            else:
                self.item.update({'itemtype': '!', 'errors': res})


    def str2hsh(self, string=str):
        """

        """
        hsh = {}

        if not string:
            return False, hsh

        at_parts = [x.strip() for x in at_regex.split(s)]
        at_tups = []
        at_entry = False
        if at_parts:
            place = -1
            tmp = at_parts.pop(0)
            hsh['itemtype'] = tmp[0]
            hsh['summary'] = tmp[1:].strip()
            at_tups.append( (hsh['itemtype'], hsh['summary'], place) )
            place += 2 + len(tmp)

            for part in at_parts:
                if part:
                    at_entry = False
                else:
                    at_entry = True
                    break
                k = part[0]
                v = part[1:].strip()
                if k in ('a', 'j', 'r'):
                    # there can be more than one entry for these keys
                    hsh.setdefault(k, []).append(v)
                else:
                    hsh[k] = v
                at_tups.append( (k, v, place) )
                place += 2 + len(part)

        for key in ['r', 'j']:
            if key not in hsh: continue
            lst = []
            for part in hsh[key]:  # an individual @r or @j entry
                amp_hsh = {}
                amp_parts = [x.strip() for x in amp_regex.split(part)]
                if amp_parts:
                    amp_hsh[key] = "".join(amp_parts.pop(0))
                    # k = amp_part
                    for part in amp_parts:  # the & keys and values for the given entry
                        if len(part) < 2:
                            continue
                        k = part[0]
                        v = part[1:].strip()
                        if v in ["''", '""']:
                            # don't add if the value was either '' or ""
                            pass
                        elif key == 'r' and k in ['M', 'e', 'm', 'w']:
                            # make these lists
                            amp_hsh[k] = comma_regex.split(v)
                        elif k == 'a':
                            amp_hsh.setdefault(k, []).append(v)
                        else:
                            amp_hsh[k] = v
                    lst.append(amp_hsh)
            hsh[key] = lst

        return hsh, at_tups, at_entry, at_parts


    def check_entry(self, string, position):
        """

        """
        hsh, at_tups, at_entry, at_parts = self.str2hsh(s)

        ask = ('say', '')
        reply = ('say', '')
        if not at_tups:
            ask = ('say', type_prompt)
            reply = ('say', item_types)
            return ask, reply 

        # itemtype, summary, end = at_tups.pop(0)
        itemtype, summary, end = at_tups[0]
        act_key = act_val = ''

        if itemtype in type_keys:
            for tup in at_tups:
                if tup[-1] < cursor_pos:
                    act_key = tup[0]
                    act_val = tup[1]
                else:
                    break

            if at_entry:
                reply_str =  "{} @-keys\n".format(type_keys[itemtype])
                current_required = ["@{}".format(x) for x in required[itemtype] if x not in hsh]
                if current_required:
                    reply_str += "  required: {}\n".format(", ".join(current_required))
                current_allowed = ["@{}".format(x) for x in allowed[itemtype] if x not in hsh or x in 'jr']
                if current_allowed:
                    reply_str += "  allowed: {}\n".format(", ".join(current_allowed))
                reply = ('say', reply_str)
            elif act_key:

                if act_key == itemtype:
                    ask = ('say', "{} summary:\n".format(type_keys[itemtype]))
                    reply = ('say', 'Enter the summary for the {} followed, optionally, by @key and value pairs\n'.format(type_keys[itemtype]))

                elif act_key in allowed[itemtype]:
                    if act_key in deal_with:
                        top, bot, obj = deal_with[act_key](hsh)
                        ask = ('say', top)
                        reply = ('say', bot + '\n')

                    elif act_val:
                        ask = ('say', "{0}: {1}\n".format(at_keys[act_key], act_val))
                    else:
                        ask = ('say', "{0}:\n".format(at_keys[act_key]))
                else:
                    ask = ('warn', "invalid @-key: '@{0}'\n".format(act_key))
            else:
                reply = ('warn', 'no act_key')

        else:
            ask = ('warn', u"invalid item type character: '{0}'\n".format(itemtype))

        # for testing and debugging:1
        reply = ('say', reply[1] + "\nat_entry {0} {1}: {2}; pos {3}\n{4}\n{5}".format(at_entry, act_key, act_val, cursor_pos, at_tups, at_parts))

        return ask, reply




    def hsh2str(self, h):
        """

        """
        pass


    def ch
